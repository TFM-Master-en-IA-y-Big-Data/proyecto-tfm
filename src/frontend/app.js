// src/frontend/app.js
let chart;

async function obtenerPrediccion() {
    const coinSelect = document.getElementById('coinSelect');
    const coin = coinSelect.value;
    const resDiv = document.getElementById('resultado');
    const boton = event.target;
    
    try {
        boton.disabled = true;
        boton.textContent = 'Cargando...';
        
        console.log(`[FRONTEND] Solicitando predicción para ${coin}...`);
        
        // Llamamos a la API
        const response = await fetch(`http://127.0.0.1:8000/predict/${coin.toLowerCase()}`);
        
        console.log(`[FRONTEND] Response status: ${response.status}`);
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || `Error HTTP ${response.status}`);
        }
        
        const data = await response.json();
        
        console.log(`[FRONTEND] Datos recibidos:`, data);
        
        // Mostramos el div de resultados
        resDiv.style.display = 'block';
        resDiv.className = data.prediction === 'Subida' ? 'subida' : 'bajada';
        
        // Llenamos los valores
        document.getElementById('resCoin').innerText = `${data.coin} - $${data.current_price.toFixed(2)}`;
        document.getElementById('resTexto').innerText = `Predicción: ${data.prediction}`;
        document.getElementById('resProb').innerText = (data.probability * 100).toFixed(1) + '%';
        document.getElementById('resRiesgo').innerText = data.risk_level;

        // Gráfica
        const ctx = document.getElementById('grafica').getContext('2d');
        if (chart) chart.destroy(); 
        
        const borderColor = data.prediction === 'Subida' ? '#28a745' : '#dc3545';
        const bgColor = data.prediction === 'Subida' ? 'rgba(40, 167, 69, 0.1)' : 'rgba(220, 53, 69, 0.1)';
        
        chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['D-6', 'D-5', 'D-4', 'D-3', 'D-2', 'D-1', 'Hoy'],
                datasets: [{
                    label: 'Precio Normalizado (%)',
                    data: data.trend_data,
                    borderColor: borderColor,
                    backgroundColor: bgColor,
                    tension: 0.4,
                    fill: true,
                    pointRadius: 4,
                    pointHoverRadius: 6
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { 
                        display: true,
                        position: 'top'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        });

    } catch (error) {
        console.error('[FRONTEND] Error:', error);
        alert("Error: " + error.message + "\n\nAsegúrate de que:\n1. FastAPI esté corriendo (puerto 8000)\n2. El pipeline esté ejecutado (python src/pipeline_maestro.py)");
    } finally {
        boton.disabled = false;
        boton.textContent = 'Predecir Tendencia';
    }
}

// Debug: Verifica que el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    console.log('[FRONTEND] DOM listo');
});