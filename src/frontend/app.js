let chart;

async function obtenerPrediccion() {
    const coin = document.getElementById('coinSelect').value;
    const resDiv = document.getElementById('resultado');
    
    try {
        // Llamamos a tu API de FastAPI
        const response = await fetch(`http://127.0.0.1:8000/predict/${coin}`);
        const data = await response.json();

        // Mostramos el div de resultados
        resDiv.style.display = 'block';
        resDiv.className = data.prediction === 'Subida' ? 'subida' : 'bajada';
        
        document.getElementById('resCoin').innerText = data.coin;
        document.getElementById('resTexto').innerText = `Predicción: ${data.prediction}`;
        document.getElementById('resProb').innerText = (data.probability * 100).toFixed(0) + '%';
        document.getElementById('resRiesgo').innerText = data.risk_level;

        
        const ctx = document.getElementById('grafica').getContext('2d');
        if (chart) chart.destroy(); 
        
        chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['D-6', 'D-5', 'D-4', 'D-3', 'D-2', 'D-1', 'Hoy'],
                datasets: [{
                    label: 'Tendencia (Simulada)',
                    data: data.trend_data,
                    borderColor: '#007bff',
                    tension: 0.1
                }]
            }
        });

    } catch (error) {
        alert("Error al conectar con el Backend. Asegúrate de que FastAPI esté corriendo.");
    }
}