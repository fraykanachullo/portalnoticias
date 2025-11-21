/* =====================================================================
   📊 admin_ia.js — Panel IA PRO 2025 (Charts + WordCloud 3D)
   ===================================================================== */

document.addEventListener("DOMContentLoaded", () => {
  initSentimentChart();
  initCategoriasChart();
  initFuentesChart();
  initWordCloud3D();
  loadAlertasIA();
  loadWordCloudFilters();


  async function loadWordCloudFilters() {
    // CATEGORÍAS
    const catSelect = document.getElementById("wc_categoria");
    const catRows = await fetchJSON("/api/stats/categorias");

    catRows?.forEach(r => {
        const op = document.createElement("option");
        op.value = r.categoria;
        op.textContent = r.categoria;
        catSelect.appendChild(op);
    });

    // FUENTES
    const fuenteSelect = document.getElementById("wc_fuente");
    const fuentes = await fetchJSON("/api/stats/fuentes");

    fuentes?.forEach(r => {
        const op = document.createElement("option");
        op.value = r.fuente;
        op.textContent = r.fuente;
        fuenteSelect.appendChild(op);
    });
}


  // 🔄 Auto-refresh cada 3 minutos (sentimiento + alertas)
  setInterval(() => {
    refreshSentimiento();
    loadAlertasIA();
  }, 180000);

  // 🌙 Toggle modo oscuro panel IA
  const themeBtn = document.getElementById("ia-theme-toggle");
  if (themeBtn) {
    themeBtn.addEventListener("click", () => {
      document.body.classList.toggle("ia-dark");
    });
  }
});

/* =====================================================================
   🌐 Helper de requests (con control de errores)
   ===================================================================== */
async function fetchJSON(url) {
  try {
    const res = await fetch(url);
    if (!res.ok) {
      console.error(`❌ Error ${res.status} en ${url}`);
      return null;
    }
    return await res.json();
  } catch (err) {
    console.error("🌐 Error de conexión:", err);
    return null;
  }
}

/* =====================================================================
   📈 1) GRÁFICO DE SENTIMIENTO
   ===================================================================== */

let sentimentChartInstance = null;

function initSentimentChart() {
  const canvas = document.getElementById("sentimentChart");
  if (!canvas) return;

  const ctx = canvas.getContext("2d");

  const pos = Number(canvas.dataset.pos || 0);
  const neg = Number(canvas.dataset.neg || 0);
  const neu = Number(canvas.dataset.neu || 0);

  sentimentChartInstance = new Chart(ctx, {
    type: "bar",
    data: {
      labels: ["Positivas", "Negativas", "Neutras"],
      datasets: [
        {
          label: "Cantidad",
          data: [pos, neg, neu],
          borderWidth: 2,
          backgroundColor: [
            "rgba(46, 204, 113, .45)",
            "rgba(231, 76, 60, .45)",
            "rgba(127, 140, 141, .45)",
          ],
          borderColor: [
            "rgba(39, 174, 96,1)",
            "rgba(192, 57, 43,1)",
            "rgba(52, 73, 94,1)",
          ],
        },
      ],
    },
    options: {
      animation: {
        duration: 900,
        easing: "easeOutExpo",
      },
      plugins: {
        legend: { display: false },
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: { precision: 0 },
        },
      },
    },
  });
}

async function refreshSentimiento() {
  const data = await fetchJSON("/api/stats/sentimiento");
  if (!data || !sentimentChartInstance) return;

  sentimentChartInstance.data.datasets[0].data = [
    data.positivos,
    data.negativos,
    data.neutros,
  ];

  sentimentChartInstance.update();
}

/* =====================================================================
   📊 2) GRÁFICO DE CATEGORÍAS (BARRAS HORIZONTALES)
   ===================================================================== */

async function initCategoriasChart() {
  const canvas = document.getElementById("categoriasChart");
  if (!canvas) return;

  const rows = await fetchJSON("/api/stats/categorias");
  if (!rows) return;

  const labels = rows.map((r) => r.categoria);
  const values = rows.map((r) => Number(r.total));

  const ctx = canvas.getContext("2d");

  new Chart(ctx, {
    type: "bar",
    data: {
      labels,
      datasets: [
        {
          label: "Noticias",
          data: values,
          backgroundColor: "rgba(52, 152, 219, .45)",
          borderColor: "rgba(41, 128, 185, 1)",
          borderWidth: 1,
        },
      ],
    },
    options: {
      indexAxis: "y",
      animation: { duration: 800, easing: "easeOutSine" },
      scales: {
        x: { beginAtZero: true },
      },
      plugins: {
        legend: { display: false },
      },
    },
  });
}

/* =====================================================================
   📰 3) GRÁFICO DE FUENTES (DOUGHNUT)
   ===================================================================== */

async function initFuentesChart() {
  const canvas = document.getElementById("fuentesChart");
  if (!canvas) return;

  const rows = await fetchJSON("/api/stats/fuentes");
  if (!rows) return;

  const labels = rows.map((r) => r.fuente);
  const values = rows.map((r) => Number(r.total));

  const ctx = canvas.getContext("2d");

  new Chart(ctx, {
    type: "doughnut",
    data: {
      labels,
      datasets: [
        {
          data: values,
          borderWidth: 1,
        },
      ],
    },
    options: {
      animation: { duration: 900, easing: "easeOutBack" },
      plugins: {
        legend: { position: "bottom" },
      },
    },
  });
}

/* =====================================================================
   🌌 4) WORDCLOUD 3D (Three.js)
   ===================================================================== */

let wcScene = null;
let wcCamera = null;
let wcRenderer = null;
let wcGroup = null;
let wcAnimationId = null;

function initWordCloud3D() {
  const container = document.getElementById("wc3d-container");
  const canvas = document.getElementById("wc3d-canvas");
  if (!container || !canvas) return;

  if (typeof THREE === "undefined") {
    console.error("Three.js no está cargado.");
    return;
  }

  const width = container.clientWidth || 300;
  const height = container.clientHeight || 300;

  // Escena
  wcScene = new THREE.Scene();

  // Cámara
  wcCamera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
  wcCamera.position.z = 220;

  // Renderer
  wcRenderer = new THREE.WebGLRenderer({
    canvas,
    alpha: true,
    antialias: true,
  });
  wcRenderer.setSize(width, height);
  wcRenderer.setPixelRatio(window.devicePixelRatio || 1);

  // Grupo donde van las palabras
  wcGroup = new THREE.Group();
  wcScene.add(wcGroup);

  // Luz suave
  const ambient = new THREE.AmbientLight(0xffffff, 1.0);
  wcScene.add(ambient);

  // Filtros + eventos
  loadWordCloudFilters();
  bindWordCloudControls();

  // Primera carga
  loadWordCloud3D();

  // Animación
  animateWordCloud();

  // Resize
  window.addEventListener("resize", onWordCloudResize);
}

function onWordCloudResize() {
  const container = document.getElementById("wc3d-container");
  if (!container || !wcRenderer || !wcCamera) return;

  const width = container.clientWidth || 300;
  const height = container.clientHeight || 300;

  wcCamera.aspect = width / height;
  wcCamera.updateProjectionMatrix();
  wcRenderer.setSize(width, height);
}

function bindWordCloudControls() {
  const btnRefresh = document.getElementById("wc-btn-refresh");
  const btnExport = document.getElementById("wc-btn-export");

  if (btnRefresh) {
    btnRefresh.addEventListener("click", () => {
      loadWordCloud3D();
    });
  }

  if (btnExport) {
    btnExport.addEventListener("click", () => {
      exportWordCloudPNG();
    });
  }
}

async function loadWordCloudFilters() {
  const catSelect = document.getElementById("wc-filter-categoria");
  const fuenteSelect = document.getElementById("wc-filter-fuente");

  if (!catSelect || !fuenteSelect) return;

  const [cats, fuentes] = await Promise.all([
    fetchJSON("/api/stats/categorias"),
    fetchJSON("/api/stats/fuentes"),
  ]);

  if (cats) {
    // limpiamos excepto "Todas"
    catSelect.innerHTML = '<option value="">Todas</option>';
    cats.forEach((c) => {
      const opt = document.createElement("option");
      opt.value = c.categoria;
      opt.textContent = c.categoria;
      catSelect.appendChild(opt);
    });
  }

  if (fuentes) {
    fuenteSelect.innerHTML = '<option value="">Todas</option>';
    fuentes.forEach((f) => {
      const opt = document.createElement("option");
      opt.value = f.fuente;
      opt.textContent = f.fuente;
      fuenteSelect.appendChild(opt);
    });
  }
}

async function loadWordCloud3D() {
  if (!wcGroup) return;

  const categoria = (document.getElementById("wc-filter-categoria")?.value || "").trim();
  const fuente = (document.getElementById("wc-filter-fuente")?.value || "").trim();
  const dias = (document.getElementById("wc-filter-dias")?.value || "").trim();
  const query = (document.getElementById("wc-filter-query")?.value || "").trim();

  const url = new URL("/api/stats/wordcloud", window.location.origin);
  if (categoria) url.searchParams.set("categoria", categoria);
  if (fuente) url.searchParams.set("fuente", fuente);
  if (dias) url.searchParams.set("dias", dias);
  if (query) url.searchParams.set("query", query);

  const data = await fetchJSON(url.toString());
  if (!data || !data.length) {
    clearWordCloud3D();
    return;
  }

  layoutWordsOnSphere(data.slice(0, 80)); // max 80 términos
}

function clearWordCloud3D() {
  if (!wcGroup) return;
  while (wcGroup.children.length > 0) {
    const obj = wcGroup.children.pop();
    if (obj.material) {
      if (obj.material.map) obj.material.map.dispose();
      obj.material.dispose();
    }
  }
}

function layoutWordsOnSphere(words) {
  if (!wcGroup || !words || !words.length) {
    clearWordCloud3D();
    return;
  }

  clearWordCloud3D();

  const N = words.length;
  const radius = 65;
  const maxWeight = Math.max(...words.map((w) => w.value || 1));

  words.forEach((w, i) => {
    const y = 1 - (i / Math.max(N - 1, 1)) * 2; // 1 → -1
    const radiusXZ = Math.sqrt(Math.max(0, 1 - y * y));
    const theta = Math.PI * (1 + Math.sqrt(5)) * i; // espiral áurea

    const x = Math.cos(theta) * radiusXZ;
    const z = Math.sin(theta) * radiusXZ;

    const sprite = createWordSprite(w.text, w.value || 1, maxWeight);
    sprite.position.set(x * radius, y * radius, z * radius);
    wcGroup.add(sprite);
  });
}

function createWordSprite(text, weight, maxWeight) {
  const canvas = document.createElement("canvas");
  const size = 256;
  canvas.width = canvas.height = size;
  const ctx = canvas.getContext("2d");

  const norm = maxWeight > 0 ? weight / maxWeight : 0.5;
  const fontSize = 26 + 18 * norm;

  ctx.clearRect(0, 0, size, size);
  ctx.font = `bold ${fontSize}px system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif`;
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";

  const gradient = ctx.createLinearGradient(0, 0, size, size);
  gradient.addColorStop(0, "#6366f1");
  gradient.addColorStop(0.5, "#22c55e");
  gradient.addColorStop(1, "#ec4899");

  ctx.fillStyle = gradient;
  ctx.shadowColor = "rgba(15,23,42,0.55)";
  ctx.shadowBlur = 18;
  ctx.shadowOffsetX = 0;
  ctx.shadowOffsetY = 0;

  ctx.fillText(text, size / 2, size / 2);

  const texture = new THREE.CanvasTexture(canvas);
  texture.minFilter = THREE.LinearFilter;

  const material = new THREE.SpriteMaterial({
    map: texture,
    transparent: true,
  });

  const sprite = new THREE.Sprite(material);
  const spriteScale = 10 + 18 * norm;
  sprite.scale.set(spriteScale, spriteScale, 1);

  return sprite;
}

function animateWordCloud() {
  if (!wcScene || !wcCamera || !wcRenderer || !wcGroup) return;

  const animate = () => {
    wcAnimationId = requestAnimationFrame(animate);
    wcGroup.rotation.y += 0.0035;
    wcGroup.rotation.x += 0.0008;
    wcRenderer.render(wcScene, wcCamera);
  };

  animate();
}

function exportWordCloudPNG() {
  if (!wcRenderer) return;

  const dataURL = wcRenderer.domElement.toDataURL("image/png");
  const link = document.createElement("a");
  link.href = dataURL;
  link.download = `wordcloud_3d_${new Date().toISOString().slice(0, 19).replace(/[:T]/g, "-")}.png`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

/* =====================================================================
   🚨 5) ALERTAS IA (RIESGOS)
   ===================================================================== */

function renderLoading(container) {
  container.innerHTML = `
    <div class="placeholder-glow">
      <div class="placeholder w-75 mb-2"></div>
      <div class="placeholder w-50 mb-2"></div>
      <div class="placeholder w-60 mb-2"></div>
    </div>`;
}

async function loadAlertasIA() {
  const container = document.getElementById("alertas-ia-list");
  if (!container) return;

  renderLoading(container);

  const rows = await fetchJSON("/api/stats/alertas");

  if (!rows) {
    container.innerHTML = `
      <p class="text-danger small mb-0">❌ Error al cargar alertas IA.</p>`;
    return;
  }

  if (!rows.length) {
    container.innerHTML = `
      <p class="text-muted small mb-0">No se han detectado alertas críticas.</p>`;
    return;
  }

  container.innerHTML = rows
    .map((r) => {
      const lvl = r.nivel;
      const badge =
        lvl === "alto"
          ? "bg-danger"
          : lvl === "medio"
          ? "bg-warning text-dark"
          : "bg-secondary";

      return `
        <div class="border-bottom py-2">
          <span class="badge ${badge} me-2 text-uppercase small">${lvl}</span>
          <strong>${r.titulo}</strong>
          <div class="small text-muted">${r.fuente} · ${r.categoria}</div>
          <div class="small text-muted">${r.fecha}</div>
        </div>`;
    })
    .join("");
}

/* ================================================================
   WORDCLOUD PRO – Filtros dinámicos + actualización
================================================================ */

async function updateWordCloud() {
    const categoria = document.getElementById("wc_categoria")?.value || "";
    const fuente = document.getElementById("wc_fuente")?.value || "";
    const dias = document.getElementById("wc_dias")?.value || "";
    const q = document.getElementById("wc_query")?.value || "";

    const img = document.getElementById("wordcloud_img");
    if (!img) return;

    // Construir URL dinámica
    const params = new URLSearchParams();

    if (categoria) params.append("categoria", categoria);
    if (fuente) params.append("fuente", fuente);
    if (dias) params.append("dias", dias);
    if (q) params.append("query", q);

    img.src = "/api/stats/wordcloud_image?" + params.toString();

    console.log("WordCloud actualizado:", img.src);
}

// Botón refresh
document.getElementById("wc_refresh")?.addEventListener("click", updateWordCloud);

// Auto load al abrir
window.addEventListener("DOMContentLoaded", updateWordCloud);

// Descargar PNG
document.getElementById("wc_download")?.addEventListener("click", () => {
    const img = document.getElementById("wordcloud_img");
    if (!img) return;
    const link = document.createElement("a");
    link.href = img.src;
    link.download = "wordcloud.png";
    link.click();
});
