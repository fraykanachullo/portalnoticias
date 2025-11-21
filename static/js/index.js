console.log("📌 index.js cargado correctamente");

// Estado global de los filtros
let fuenteActual = "";
let categoriaActual = "";
let paginaActual = 1;
let totalPaginas = 1;

// 🌙 Toggle Modo Oscuro
const toggle = document.getElementById("toggleDark");
if (localStorage.getItem("modoOscuro") === "1")
    document.body.classList.add("dark-mode");

if (toggle) {
    toggle.addEventListener("click", () => {
        document.body.classList.toggle("dark-mode");
        localStorage.setItem("modoOscuro", document.body.classList.contains("dark-mode") ? "1" : "0");

        toggle.innerHTML = document.body.classList.contains("dark-mode")
            ? '<i class="fa-solid fa-sun"></i> Modo claro'
            : '<i class="fa-solid fa-moon"></i> Modo oscuro';
    });
}

// 🔄 Cargar Noticias filtradas
function actualizarNoticias() {
    fetch(`/api/noticias?fuente=${fuenteActual}&categoria=${categoriaActual}&page=${paginaActual}&per_page=10`)
        .then(r => r.json())
        .then(res => {
            const cont = document.getElementById("contenido-noticias");
            const pag = document.getElementById("pagination");

            cont.innerHTML = "";
            pag.innerHTML = "";

            if (!res.data || res.data.length === 0) {
                cont.innerHTML = "<div class='col-12 text-center text-muted'><em>No se encontraron noticias.</em></div>";
                return;
            }

            res.data.forEach(n => {
                cont.innerHTML += `
                <div class="col-md-6 col-lg-4 mb-4">
                    <div class="card news-card h-100">
                        <img src="${n.url_imagen || 'https://via.placeholder.com/400x200?text=Sin+imagen'}">
                        <div class="card-body">
                            <h6>${n.titulo}</h6>
                            <p class="text-muted small mb-2">${n.fuente} — ${n.categoria || ''}</p>
                            <a href="${n.url_noticia}" target="_blank" class="btn btn-sm btn-outline-danger">Leer más</a>
                        </div>
                    </div>
                </div>`;
            });

            totalPaginas = res.pages;
            generarPaginacion();
        });
}

// 🔢 Generar paginación
function generarPaginacion() {
    const pag = document.getElementById("pagination");
    for (let i = 1; i <= totalPaginas; i++) {
        pag.innerHTML += `
            <li class="page-item ${i === paginaActual ? 'active' : ''}">
                <a href="#" class="page-link" onclick="cambiarPagina(${i})">${i}</a>
            </li>`;
    }
}

function cambiarPagina(num) {
    paginaActual = num;
    actualizarNoticias();
}

// 🎯 Selección de filtros
document.addEventListener("DOMContentLoaded", () => {

    // Filtros por fuente
    document.querySelectorAll("#fuente-filtros .btn-filter").forEach(btn => {
        btn.addEventListener("click", () => {
            documento.querySelectorAll("#fuente-filtros .btn-filter").forEach(b => b.classList.remove("active"));
            btn.classList.add("active");

            fuenteActual = btn.dataset.fuente;
            paginaActual = 1;
            actualizarNoticias();
        });
    });

    // Filtros por categoría
    document.querySelectorAll("#categoria-filtros .btn-filter").forEach(btn => {
        btn.addEventListener("click", () => {
            document.querySelectorAll("#categoria-filtros .btn-filter").forEach(b => b.classList.remove("active"));
            btn.classList.add("active");

            categoriaActual = btn.dataset.categoria;
            paginaActual = 1;
            actualizarNoticias();
        });
    });

    cargarFacebook();
});

// 🔵 Cargar Facebook
function cargarFacebook() {
    fetch("/api/facebook?limit=5")
        .then(r => r.json())
        .then(data => {
            const fb = document.getElementById("fb-posts");
            fb.innerHTML = "";

            if (!data || data.length === 0) {
                fb.innerHTML = "<div class='text-center text-muted small'>Sin publicaciones recientes.</div>";
                return;
            }

            data.forEach(p => {
                fb.innerHTML += `
                <div class="fb-item">
                    <img src="${p.url_imagen || 'https://via.placeholder.com/80x60?text=FB'}">
                    <div>
                        <h6>${p.titulo}</h6>
                        <small class="text-muted">${new Date(p.fecha_publicacion).toLocaleDateString()}</small><br>
                        <a href="${p.url}" target="_blank" class="text-danger small">Ver más</a>
                    </div>
                </div>`;
            });
        });
}
