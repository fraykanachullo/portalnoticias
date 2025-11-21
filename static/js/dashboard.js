document.addEventListener('DOMContentLoaded', async function() {
    // Cargar estadísticas
    await cargarEstadisticasRapidas();
    await cargarSentimientoDominante();
    await cargarUltimasNoticias();

    // Configurar WebSocket
    iniciarWebSocket();
});

async function cargarEstadisticasRapidas() {
    try {
        const response = await fetch('/api/stats/general');
        const stats = await response.json();
        document.getElementById('stat-noticias').textContent = stats.total_noticias;
        document.getElementById('stat-fuentes').textContent = stats.total_fuentes;
        document.getElementById('stat-categorias').textContent = stats.total_categorias;
    } catch (error) {
        console.error('Error cargando estadísticas', error);
    }
}

async function cargarSentimientoDominante() {
    try {
        const response = await fetch('/api/stats/sentimiento');
        const sentimiento = await response.json();
        document.getElementById('stat-sentimiento').textContent = sentimiento.positivos > sentimiento.negativos ? 'Positivo' : 'Negativo';
    } catch (error) {
        console.error('Error cargando sentimiento', error);
    }
}

async function cargarUltimasNoticias() {
    try {
        const response = await fetch('/api/noticias');
        const data = await response.json();
        const container = document.getElementById('noticias-container');
        container.innerHTML = data.data.map(noticia => `
            <div class="noticia-card">
                <h5>${noticia.titulo}</h5>
                <p>${noticia.descripcion}</p>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error cargando noticias', error);
    }
}

// WebSocket para notificaciones
function iniciarWebSocket() {
    const ws = new WebSocket("ws://127.0.0.1:5000/ws/noticias");
    ws.onmessage = function(event) {
        const data = JSON.parse(event.data);
        // Mostrar notificación de nueva noticia
        alert("Nueva Noticia: " + data.titulo); // Puedes personalizar cómo mostrar la notificación
    }
}
