{% extends "user/user_layout.html" %}

{% block title %}Dashboard - Noticias 2025{% endblock %}

{% block content %}
<h2 class="fw-bold mb-4">
    <i class="fa-solid fa-chart-line"></i> Panel de Usuario
</h2>

<div class="row">
    <!-- Card de Noticias Totales -->
    <div class="col-md-4 mb-4">
        <div class="card shadow-sm p-3">
            <h5><i class="fa-solid fa-newspaper text-danger"></i> Noticias Totales</h5>
            <p id="stat-noticias">{{ stats.total_noticias }}</p>
        </div>
    </div>

    <!-- Card de Análisis de Sentimiento -->
    <div class="col-md-4 mb-4">
        <div class="card shadow-sm p-3">
            <h5><i class="fa-solid fa-heart text-success"></i> Análisis de Sentimiento</h5>
            <p id="stat-sentimiento">{{ 'Positivo' if sentimiento['positivos'] > sentimiento['negativos'] else 'Negativo' }}</p>
        </div>
    </div>

    <!-- Card de Últimas Noticias -->
    <div class="col-md-4 mb-4">
        <div class="card shadow-sm p-3">
            <h5><i class="fa-solid fa-newspaper"></i> Últimas Noticias</h5>
            <ul>
                {% for noticia in ultimas_noticias %}
                    <li><a href="{{ noticia.url_noticia }}" target="_blank">{{ noticia.titulo }}</a></li>
                {% endfor %}
            </ul>
        </div>
    </div>
</div>
{% endblock %}
