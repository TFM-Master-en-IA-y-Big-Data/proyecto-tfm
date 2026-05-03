import { auth } from "./Firebase.config.js";
import {
  createUserWithEmailAndPassword,
  onAuthStateChanged,
  signInWithEmailAndPassword,
  signOut,
  updateProfile,
} from "https://www.gstatic.com/firebasejs/10.12.5/firebase-auth.js";

let chart;
let marketIntervalId = null;
let sparklineCharts = new Map();
let marketData = [];

function el(id) {
  return document.getElementById(id);
}

function setText(id, value) {
  el(id).textContent = value;
}

function setError(id, message) {
  setText(id, message || "");
}

function setBusy(button, busy, busyText, idleText) {
  button.disabled = busy;
  button.textContent = busy ? busyText : idleText;
}

function getAllowedCoins() {
  const select = el("coinSelect");
  if (!select) return [];
  return Array.from(select.options).map((o) => o.value);
}

function formatUSD(value) {
  if (typeof value !== "number" || Number.isNaN(value)) return "-";
  return value.toLocaleString(undefined, {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: value >= 1 ? 2 : 8,
  });
}

function clearSparklines() {
  for (const chart of sparklineCharts.values()) {
    try {
      chart.destroy();
    } catch {}
  }
  sparklineCharts = new Map();
}

function setMarketStatus(text, variant = "info") {
  const badge = el("marketStatus");
  if (!badge) return;
  badge.textContent = text;

  if (variant === "error") {
    badge.style.background = "rgba(239, 68, 68, 0.10)";
    badge.style.color = "rgba(239, 68, 68, 0.95)";
    badge.style.borderColor = "rgba(239, 68, 68, 0.18)";
    return;
  }

  badge.style.background = "rgba(37, 99, 235, 0.10)";
  badge.style.color = "rgba(37, 99, 235, 0.90)";
  badge.style.borderColor = "rgba(37, 99, 235, 0.20)";
}

function renderMarketList() {
  const list = el("marketList");
  if (!list) return;

  const query = (el("marketSearch")?.value || "").trim().toLowerCase();
  const allowedSet = new Set(getAllowedCoins());

  const filtered = query
    ? marketData.filter((c) => {
        const name = (c.name || "").toLowerCase();
        const symbol = (c.symbol || "").toLowerCase();
        return name.includes(query) || symbol.includes(query);
      })
    : marketData;

  list.innerHTML = "";
  clearSparklines();

  if (!filtered.length) {
    const empty = document.createElement("div");
    empty.className = "hint";
    empty.textContent = "No hay resultados para esa búsqueda.";
    list.appendChild(empty);
    return;
  }

  filtered.forEach((coin) => {
    const row = document.createElement("div");
    row.className = "market-row";
    row.dataset.coinId = coin.id;

    const pct = Number(coin.price_change_percentage_24h);
    const pctOk = Number.isFinite(pct);
    const pctClass = pctOk && pct >= 0 ? "positive" : "negative";
    const pctText = pctOk ? `${pct >= 0 ? "▲" : "▼"} ${Math.abs(pct).toFixed(2)}%` : "-";

    const supported = allowedSet.has(coin.id);
    const hintText = supported ? "Predicción disponible" : "Predicción no disponible";

    row.innerHTML = `
      <div class="mr-rank">${coin.market_cap_rank ?? "-"}</div>
      <div class="mr-coin">
        <img src="${coin.image}" alt="" />
        <div class="mr-coin-text">
          <div class="mr-coin-name">${coin.name} <span style="font-weight:700;color:rgba(15,23,42,0.45);font-size:12px;">· ${hintText}</span></div>
          <div class="mr-coin-symbol">${(coin.symbol || "").toUpperCase()}</div>
        </div>
      </div>
      <div class="mr-price">${formatUSD(coin.current_price)}</div>
      <div class="mr-change ${pctClass}">${pctText}</div>
      <div class="mr-chart"><canvas id="spark-${coin.id}"></canvas></div>
    `;

    row.addEventListener("click", () => {
      setError("marketError", "");
      setText("marketHint", "");

      if (!supported) {
        setText(
          "marketHint",
          "Esta cripto aún no tiene predicción en el modelo. Selecciona una de las criptos soportadas (Bitcoin, Ethereum, Solana, BNB, Ripple)."
        );
        return;
      }

      el("coinSelect").value = coin.id;
      setText("marketHint", `Seleccionada: ${coin.name}. Ya puedes predecir en el panel de la izquierda.`);
      window.scrollTo({ top: 0, behavior: "smooth" });
    });

    list.appendChild(row);

    const spark = coin?.sparkline_in_7d?.price;
    if (Array.isArray(spark) && spark.length) {
      const color = pctOk && pct >= 0 ? "#10b981" : "#ef4444";
      const canvas = row.querySelector(`#spark-${coin.id}`);
      const ctx = canvas.getContext("2d");
      const c = new window.Chart(ctx, {
        type: "line",
        data: {
          labels: spark.map((_, i) => i),
          datasets: [
            {
              data: spark,
              borderColor: color,
              borderWidth: 2,
              pointRadius: 0,
              fill: false,
              tension: 0.4,
            },
          ],
        },
        options: {
          events: [],
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: false }, tooltip: { enabled: false } },
          scales: { x: { display: false }, y: { display: false } },
        },
      });
      sparklineCharts.set(coin.id, c);
    }
  });
}

async function updateMarket() {
  try {
    setMarketStatus("Actualizando…");
    const url =
      "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=100&page=1&sparkline=true&price_change_percentage=24h";
    const response = await fetch(url);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data = await response.json();
    if (!Array.isArray(data)) throw new Error("Respuesta inválida");

    marketData = data;
    setError("marketError", "");
    setMarketStatus("En vivo");
    renderMarketList();
  } catch (error) {
    setMarketStatus("Sin conexión", "error");
    setError(
      "marketError",
      "No se pudo cargar el market (CoinGecko). Inténtalo de nuevo en unos segundos."
    );
  }
}

function startMarket() {
  if (marketIntervalId) return;
  if (!el("marketList")) return;

  updateMarket();
  marketIntervalId = window.setInterval(updateMarket, 20000);
}

function stopMarket() {
  if (marketIntervalId) {
    window.clearInterval(marketIntervalId);
    marketIntervalId = null;
  }
  clearSparklines();
  marketData = [];
  const list = el("marketList");
  if (list) list.innerHTML = "";
  setError("marketError", "");
  setText("marketHint", "");
  setMarketStatus("Pausado");
}

function syncEmailBetweenForms(fromMode, toMode) {
  const fromId = fromMode === "login" ? "loginEmail" : "registerEmail";
  const toId = toMode === "login" ? "loginEmail" : "registerEmail";
  const fromValue = el(fromId)?.value?.trim?.() || "";
  if (fromValue) el(toId).value = fromValue;
}

function errorMessageFromAuth(error, mode) {
  const code = error?.code || "";

  if (code === "auth/network-request-failed") {
    return "No hay conexión. Revisa tu red e inténtalo de nuevo.";
  }
  if (code === "auth/too-many-requests") {
    return "Demasiados intentos. Espera un momento y vuelve a intentarlo.";
  }
  if (code === "auth/invalid-email") {
    return "El correo no es válido.";
  }

  if (mode === "register") {
    if (code === "auth/email-already-in-use") {
      return "El correo ya está en uso. Prueba a iniciar sesión.";
    }
    if (code === "auth/weak-password") {
      return "La contraseña es demasiado débil. Usa al menos 6 caracteres.";
    }
    if (code === "auth/operation-not-allowed") {
      return "El registro con correo/contraseña no está habilitado en Firebase.";
    }
    return "No se pudo crear la cuenta. Revisa los datos e inténtalo de nuevo.";
  }

  if (mode === "login") {
    if (code === "auth/invalid-credential" || code === "auth/wrong-password" || code === "auth/user-not-found") {
      return "Correo o contraseña incorrectos.";
    }
    if (code === "auth/user-disabled") {
      return "Esta cuenta está deshabilitada.";
    }
    return "No se pudo iniciar sesión. Revisa los datos e inténtalo de nuevo.";
  }

  return "Ha ocurrido un error. Inténtalo de nuevo.";
}

function setAuthMode(mode, options = {}) {
  const loginForm = el("loginForm");
  const registerForm = el("registerForm");
  const authSwitch = el("authSwitch");

  const isLogin = mode === "login";
  loginForm.hidden = !isLogin;
  registerForm.hidden = isLogin;

  if (authSwitch) authSwitch.checked = !isLogin;

  setError("loginError", "");
  setError("registerError", "");

  if (options?.syncEmailFrom && options?.syncEmailFrom !== mode) {
    syncEmailBetweenForms(options.syncEmailFrom, mode);
  }

  if (options?.focus !== false) {
    const focusId = isLogin ? "loginEmail" : "registerNombre";
    el(focusId)?.focus?.();
  }
}

async function handleRegister(event) {
  event.preventDefault();

  const submit = el("registerSubmit");
  setBusy(submit, true, "Creando cuenta...", "Crear cuenta");
  setError("registerError", "");

  const nombre = el("registerNombre").value.trim();
  const apellidos = el("registerApellidos").value.trim();
  const email = el("registerEmail").value.trim();
  const password = el("registerPassword").value;

  try {
    const credential = await createUserWithEmailAndPassword(auth, email, password);
    const displayName = `${nombre} ${apellidos}`.trim();
    if (displayName) await updateProfile(credential.user, { displayName });
    el("registerPassword").value = "";
  } catch (error) {
    const msg = errorMessageFromAuth(error, "register");
    setError("registerError", msg);
    if (error?.code === "auth/email-already-in-use") {
      setAuthMode("login", { syncEmailFrom: "register" });
    }
  } finally {
    setBusy(submit, false, "Creando cuenta...", "Crear cuenta");
  }
}

async function handleLogin(event) {
  event.preventDefault();

  const submit = el("loginSubmit");
  setBusy(submit, true, "Entrando...", "Iniciar sesión");
  setError("loginError", "");

  const email = el("loginEmail").value.trim();
  const password = el("loginPassword").value;

  try {
    await signInWithEmailAndPassword(auth, email, password);
    el("loginPassword").value = "";
  } catch (error) {
    setError("loginError", errorMessageFromAuth(error, "login"));
  } finally {
    setBusy(submit, false, "Entrando...", "Iniciar sesión");
  }
}

async function handleLogout() {
  await signOut(auth);
}

async function obtenerPrediccion() {
  const coinSelect = el("coinSelect");
  const coin = coinSelect.value;
  const resDiv = el("resultado");
  const boton = el("predictButton");

  if (!auth.currentUser) {
    alert("Necesitas iniciar sesión para usar la predicción.");
    return;
  }

  try {
    setBusy(boton, true, "Cargando...", "Predecir Tendencia");

    const response = await fetch(`http://127.0.0.1:8000/predict/${coin.toLowerCase()}`);

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || `Error HTTP ${response.status}`);
    }

    const data = await response.json();

    resDiv.style.display = "block";
    resDiv.className = data.prediction === "Subida" ? "subida" : "bajada";

    el("resCoin").innerText = `${data.coin} - $${data.current_price.toFixed(2)}`;
    el("resTexto").innerText = `Predicción: ${data.prediction}`;
    el("resProb").innerText = (data.probability * 100).toFixed(1) + "%";
    el("resRiesgo").innerText = data.risk_level;

    const ctx = el("grafica").getContext("2d");
    if (chart) chart.destroy();

    const borderColor = data.prediction === "Subida" ? "#28a745" : "#dc3545";
    const bgColor =
      data.prediction === "Subida"
        ? "rgba(40, 167, 69, 0.1)"
        : "rgba(220, 53, 69, 0.1)";

    chart = new window.Chart(ctx, {
      type: "line",
      data: {
        labels: ["D-6", "D-5", "D-4", "D-3", "D-2", "D-1", "Hoy"],
        datasets: [
          {
            label: "Precio Normalizado (%)",
            data: data.trend_data,
            borderColor,
            backgroundColor: bgColor,
            tension: 0.4,
            fill: true,
            pointRadius: 4,
            pointHoverRadius: 6,
          },
        ],
      },
      options: {
        responsive: true,
        plugins: {
          legend: {
            display: true,
            position: "top",
          },
        },
        scales: {
          y: {
            beginAtZero: true,
            max: 100,
          },
        },
      },
    });
  } catch (error) {
    alert(
      "Error: " +
        (error?.message || "Error inesperado") +
        "\n\nAsegúrate de que:\n1. FastAPI esté corriendo (puerto 8000)\n2. El pipeline esté ejecutado (python src/pipeline_maestro.py)"
    );
  } finally {
    setBusy(boton, false, "Cargando...", "Predecir Tendencia");
  }
}

document.addEventListener("DOMContentLoaded", () => {
  setAuthMode("login", { focus: false });

  const authSwitch = el("authSwitch");
  if (authSwitch) {
    authSwitch.addEventListener("change", () => {
      const mode = authSwitch.checked ? "register" : "login";
      setAuthMode(mode, { syncEmailFrom: mode === "login" ? "register" : "login" });
    });
  }

  el("loginForm").addEventListener("submit", handleLogin);
  el("registerForm").addEventListener("submit", handleRegister);

  el("logoutButton").addEventListener("click", handleLogout);
  el("predictButton").addEventListener("click", obtenerPrediccion);
  el("marketSearch")?.addEventListener("input", () => renderMarketList());

  onAuthStateChanged(auth, (user) => {
    const authCard = el("authCard");
    const appCard = el("appCard");

    if (user) {
      authCard.hidden = true;
      appCard.hidden = false;
      setText("userEmail", user.email || user.displayName || "");
      setError("loginError", "");
      setError("registerError", "");
      startMarket();
    } else {
      authCard.hidden = false;
      appCard.hidden = true;
      setText("userEmail", "");
      el("loginPassword").value = "";
      el("registerPassword").value = "";
      el("resultado").style.display = "none";
      stopMarket();
    }
  });
});
