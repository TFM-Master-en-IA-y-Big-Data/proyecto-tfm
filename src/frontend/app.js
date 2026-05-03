import { auth } from "./Firebase.config.js";
import {
  createUserWithEmailAndPassword,
  onAuthStateChanged,
  signInWithEmailAndPassword,
  signOut,
  updateProfile,
} from "https://www.gstatic.com/firebasejs/10.12.5/firebase-auth.js";

let chart;

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

  onAuthStateChanged(auth, (user) => {
    const authCard = el("authCard");
    const appCard = el("appCard");

    if (user) {
      authCard.hidden = true;
      appCard.hidden = false;
      setText("userEmail", user.email || user.displayName || "");
      setError("loginError", "");
      setError("registerError", "");
    } else {
      authCard.hidden = false;
      appCard.hidden = true;
      setText("userEmail", "");
      el("loginPassword").value = "";
      el("registerPassword").value = "";
      el("resultado").style.display = "none";
    }
  });
});
