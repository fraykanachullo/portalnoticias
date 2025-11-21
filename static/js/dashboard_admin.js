/* ============================================================================
   📊 dashboard_admin.js — Dashboard Admin ULTRA PRO 2025
   ============================================================================ */

document.addEventListener("DOMContentLoaded", () => {
  initCategoriasChart();
  initFuentesChart();
  initSentimientoDoughnut();  // CAMBIADO A DONUT PREMIUM
  initNoticiasDiaChart();
  loadWordCloudMini();
});

/* ============================================================================
   🌐 Helper genérico para fetch → JSON
   ============================================================================ */
async function fetchJSON(url) {
  try {
    const res = await fetch(url);
    if (!res.ok) return null;
    return await res.json();
  } catch (err) {
    console.error("❌ Error de conexión:", err);
    return null;
  }
}

/* ============================================================================
   1) Noticias por categoría — Barras horizontales
   ============================================================================ */
async function initCategoriasChart() {
  const canvas = document.getElementById("chartCategorias");
  if (!canvas) return;

  const rows = await fetchJSON("/api/stats/categorias");
  if (!rows) return;

  new Chart(canvas.getContext("2d"), {
    type: "bar",
    data: {
      labels: rows.map(r => r.categoria),
      datasets: [{
        label: "Noticias",
        data: rows.map(r => r.total),
        backgroundColor: "rgba(52,152,219,.45)",
        borderColor: "rgba(41,128,185,1)",
        borderWidth: 1
      }]
    },
    options: {
      indexAxis: "y",
      animation: { duration: 800 },
      plugins: { legend: { display: false } }
    }
  });
}

/* ============================================================================
   2) Noticias por fuente — Barras verticales
   ============================================================================ */
async function initFuentesChart() {
  const canvas = document.getElementById("chartFuentes");
  if (!canvas) return;

  const rows = await fetchJSON("/api/stats/fuentes");
  if (!rows) return;

  new Chart(canvas.getContext("2d"), {
    type: "bar",
    data: {
      labels: rows.map(r => r.fuente),
      datasets: [{
        label: "Noticias",
        data: rows.map(r => r.total),
        backgroundColor: "rgba(231,76,60,.25)",
        borderColor: "rgba(192,57,43,1)",
        borderWidth: 1
      }]
    },
    options: {
      animation: { duration: 800 },
      plugins: { legend: { display: false } },
      scales: { y: { beginAtZero: true } }
    }
  });
}

/* ============================================================================
   3) Sentimiento — DONUT PREMIUM
   ============================================================================ */
async function initSentimientoDoughnut() {
  const canvas = document.getElementById("chartSentimiento");
  if (!canvas) return;

  const data = await fetchJSON("/api/stats/sentimiento");
  if (!data) return;

  new Chart(canvas.getContext("2d"), {
    type: "doughnut",
    data: {
      labels: ["Positivas", "Negativas", "Neutras"],
      datasets: [{
        data: [data.positivos, data.negativos, data.neutros],
        backgroundColor: [
          "rgba(46,204,113,0.78)",
          "rgba(231,76,60,0.78)",
          "rgba(127,140,141,0.78)"
        ],
        hoverOffset: 12,
        borderWidth: 2
      }]
    },
    options: {
      cutout: "62%",
      rotation: -30,
      plugins: {
        legend: {
          position: "bottom",
          labels: { boxWidth: 18, padding: 16 }
        }
      }
    }
  });
}

/* ============================================================================
   4) Noticias por día — Línea Profesional (últimos 30 días)
   ============================================================================ */
async function initNoticiasDiaChart() {
  const canvas = document.getElementById("chartNoticiasDia");
  if (!canvas) return;

  const rows = await fetchJSON("/api/stats/noticias_dia");
  if (!rows) return;

  const labels = rows.map(r => {
    let [y, m, d] = r.fecha.split("-");
    return `${d}/${m}`;
  });

  new Chart(canvas.getContext("2d"), {
    type: "line",
    data: {
      labels,
      datasets: [{
        label: "Noticias por día",
        data: rows.map(r => r.total),
        fill: true,
        tension: 0.35,
        borderColor: "rgba(52,152,219,1)",
        backgroundColor: "rgba(52,152,219,.20)",
        borderWidth: 3,
        pointBackgroundColor: "rgba(41,128,185,1)",
      }]
    },
    options: {
      plugins: { legend: { display: false } },
      scales: {
        y: { beginAtZero: true },
        x: { ticks: { maxRotation: 0 } }
      }
    }
  });
}

/* ============================================================================
   5) WordCloud mini — Premium Style
   ============================================================================ */
async function loadWordCloudMini() {
  const container = document.getElementById("wordcloudContainer");
  if (!container) return;

  container.innerHTML = `<small class="text-muted">Cargando...</small>`;

  const rows = await fetchJSON("/api/stats/wordcloud?dias=7");
  if (!rows || !rows.length) {
    container.innerHTML = `<small class="text-muted">Sin datos suficientes</small>`;
    return;
  }

  const values = rows.map(r => r.value);
  const min = Math.min(...values);
  const max = Math.max(...values);

  const scale = value => 0.85 + (1.9 - 0.85) * ((value - min) / (max - min));

  const palette = [
    "#34495e", "#2980b9", "#16a085", "#8e44ad",
    "#d35400", "#c0392b", "#27ae60", "#2c3e50"
  ];

  container.innerHTML = rows.map((r, i) => `
    <span style="
      font-size:${scale(r.value)}rem;
      margin:4px;
      color:${palette[i % palette.length]};
      display:inline-block;
      text-shadow:1px 1px 1px rgba(0,0,0,.12);
    ">
      ${r.text}
    </span>
  `).join("");
}
