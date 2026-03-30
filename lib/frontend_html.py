FRONTEND_HTML = """
<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Score API - Gestao Manual e Automatica</title>
  <link
    rel="stylesheet"
    href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
    integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY="
    crossorigin=""
  />
  <style>
    :root {
      --bg: #eef4f7;
      --panel: #ffffff;
      --panel-alt: #f7fbfc;
      --text: #10243d;
      --subtle: #5b7088;
      --border: #d7e1ea;
      --primary: #0b7285;
      --primary-strong: #0f5c73;
      --accent: #ff9f1c;
      --danger: #b42318;
      --success: #12703d;
      --shadow: 0 16px 38px rgba(16, 36, 61, 0.08);
      --radius: 18px;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      color: var(--text);
      font-family: "Segoe UI", Tahoma, sans-serif;
      background:
        radial-gradient(circle at top left, rgba(11, 114, 133, 0.12), transparent 28%),
        radial-gradient(circle at right bottom, rgba(255, 159, 28, 0.12), transparent 22%),
        linear-gradient(180deg, #f8fbfd 0%, var(--bg) 100%);
    }
    .container {
      max-width: 1380px;
      margin: 0 auto;
      padding: 20px;
    }
    .panel {
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 16px;
      box-shadow: var(--shadow);
    }
    .hero {
      display: grid;
      grid-template-columns: 1.1fr 0.9fr;
      gap: 16px;
      margin-bottom: 16px;
    }
    .hero-card {
      display: flex;
      flex-direction: column;
      gap: 14px;
      min-height: 100%;
      background: linear-gradient(135deg, rgba(11, 114, 133, 0.08), rgba(255, 255, 255, 0.95));
    }
    h1, h2, h3 { margin: 0; }
    .muted { color: var(--subtle); }
    .hero-metrics {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
    }
    .metric {
      min-width: 140px;
      padding: 12px 14px;
      border-radius: 14px;
      background: rgba(255, 255, 255, 0.88);
      border: 1px solid rgba(11, 114, 133, 0.1);
    }
    .metric strong {
      display: block;
      font-size: 22px;
      margin-top: 4px;
    }
    .tab-bar {
      display: inline-flex;
      flex-wrap: wrap;
      gap: 8px;
      padding: 6px;
      border-radius: 999px;
      background: rgba(16, 36, 61, 0.06);
      border: 1px solid rgba(16, 36, 61, 0.05);
      align-self: flex-start;
    }
    .tab-btn {
      border: 0;
      border-radius: 999px;
      padding: 11px 16px;
      cursor: pointer;
      font-size: 14px;
      font-weight: 600;
      color: var(--subtle);
      background: transparent;
      transition: 0.2s ease;
    }
    .tab-btn.active {
      color: #fff;
      background: linear-gradient(135deg, var(--primary), var(--primary-strong));
      box-shadow: 0 8px 20px rgba(11, 114, 133, 0.22);
    }
    .hero-note {
      padding: 12px 14px;
      border-radius: 14px;
      background: rgba(255, 255, 255, 0.9);
      border: 1px dashed rgba(11, 114, 133, 0.24);
      font-size: 14px;
      color: var(--subtle);
    }
    #map {
      width: 100%;
      height: 58vh;
      min-height: 380px;
      border-radius: 16px;
      border: 1px solid var(--border);
      overflow: hidden;
    }
    .grid {
      display: grid;
      grid-template-columns: 1.1fr 0.9fr;
      gap: 16px;
    }
    .list-head,
    .editor-head {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 12px;
      margin-bottom: 12px;
    }
    .pill {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 6px 10px;
      border-radius: 999px;
      background: var(--panel-alt);
      border: 1px solid var(--border);
      font-size: 12px;
      color: var(--subtle);
    }
    .badge {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 6px 10px;
      border-radius: 999px;
      font-size: 12px;
      font-weight: 600;
      background: rgba(11, 114, 133, 0.09);
      color: var(--primary-strong);
    }
    .badge.manual {
      background: rgba(255, 159, 28, 0.14);
      color: #965a00;
    }
    .badge.automatic {
      background: rgba(11, 114, 133, 0.12);
      color: var(--primary-strong);
    }
    table {
      width: 100%;
      border-collapse: collapse;
      font-size: 14px;
    }
    th, td {
      text-align: left;
      padding: 12px 8px;
      border-bottom: 1px solid var(--border);
      vertical-align: top;
    }
    th { color: var(--subtle); font-weight: 600; }
    .name-cell {
      display: grid;
      gap: 4px;
    }
    .mini {
      font-size: 12px;
      color: var(--subtle);
    }
    .row-actions {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }
    button {
      border: 0;
      border-radius: 10px;
      padding: 9px 12px;
      cursor: pointer;
      background: #e9eff4;
      font-size: 13px;
      color: var(--text);
      transition: transform 0.14s ease, box-shadow 0.14s ease, background 0.14s ease;
    }
    button:hover {
      transform: translateY(-1px);
      box-shadow: 0 8px 20px rgba(16, 36, 61, 0.09);
    }
    button.primary {
      background: linear-gradient(135deg, var(--primary), var(--primary-strong));
      color: #fff;
    }
    button.warning {
      background: #fff4df;
      color: #8a5600;
    }
    button.danger {
      background: var(--danger);
      color: #fff;
    }
    .form-panel {
      display: none;
      gap: 12px;
    }
    .form-panel.active {
      display: grid;
    }
    .form-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 10px;
    }
    .form-grid.triple {
      grid-template-columns: 1fr 1fr 120px;
    }
    .form-grid.full {
      grid-template-columns: 1fr;
    }
    label {
      display: block;
      margin-bottom: 5px;
      font-size: 12px;
      color: var(--subtle);
    }
    input, textarea, select {
      width: 100%;
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 10px 12px;
      font-size: 14px;
      font-family: inherit;
      background: #fff;
      color: var(--text);
    }
    .color-field {
      display: flex;
      flex-direction: column;
      align-items: flex-start;
    }
    .color-picker {
      width: 52px;
      min-width: 52px;
      height: 42px;
      padding: 4px;
      border-radius: 999px;
      border: 1px solid var(--border);
      background: #fff;
      cursor: pointer;
      overflow: hidden;
    }
    .color-picker::-webkit-color-swatch-wrapper {
      padding: 0;
    }
    .color-picker::-webkit-color-swatch {
      border: 0;
      border-radius: 999px;
    }
    .color-picker::-moz-color-swatch {
      border: 0;
      border-radius: 999px;
    }
    .area-name-line {
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .color-dot {
      width: 12px;
      height: 12px;
      border-radius: 999px;
      border: 1px solid rgba(16, 36, 61, 0.12);
      flex: 0 0 auto;
    }
    textarea {
      min-height: 180px;
      resize: vertical;
    }
    .status {
      min-height: 20px;
      font-size: 13px;
      font-weight: 600;
    }
    .note-box {
      padding: 12px 14px;
      border-radius: 14px;
      background: var(--panel-alt);
      border: 1px solid var(--border);
      font-size: 13px;
      color: var(--subtle);
      line-height: 1.45;
    }
    pre {
      margin: 10px 0 0;
      padding: 14px;
      border-radius: 16px;
      background: #0f172a;
      color: #dbeafe;
      max-height: 260px;
      overflow: auto;
      font-size: 12px;
    }
    .section-title {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      margin-top: 6px;
    }
    .hidden {
      display: none !important;
    }
    @media (max-width: 1080px) {
      .hero,
      .grid {
        grid-template-columns: 1fr;
      }
      #map {
        height: 46vh;
        min-height: 330px;
      }
    }
    @media (max-width: 740px) {
      .container { padding: 14px; }
      .form-grid { grid-template-columns: 1fr; }
      .list-head,
      .editor-head {
        flex-direction: column;
      }
      .hero-metrics {
        display: grid;
        grid-template-columns: 1fr 1fr;
      }
      .row-actions button {
        flex: 1 1 120px;
      }
    }
  </style>
</head>
<body>
  <div class="container">
    <section class="hero">
      <div class="panel hero-card">
        <div>
          <h1>Gestao de Areas</h1>
          <p class="muted" style="margin:8px 0 0;">
            Separe a operacao em modo manual e automatico sem perder o mesmo JSON do object store.
          </p>
        </div>
        <div class="tab-bar" id="mode-tabs">
          <button class="tab-btn active" id="tab-manual" type="button">Manual</button>
          <button class="tab-btn" id="tab-automatic" type="button">Automatico</button>
        </div>
        <div class="hero-metrics">
          <div class="metric">
            <span class="mini">Areas visiveis</span>
            <strong id="metric-visible">0</strong>
          </div>
          <div class="metric">
            <span class="mini">Total geral</span>
            <strong id="metric-total">0</strong>
          </div>
          <div class="metric">
            <span class="mini">Automaticas</span>
            <strong id="metric-automatic">0</strong>
          </div>
        </div>
        <div class="hero-note" id="mode-note">
          No modo manual, o fluxo continua igual ao atual: polygons em JSON, preview local e CRUD direto.
        </div>
      </div>
      <div class="panel">
        <div class="list-head" style="margin-bottom:12px;">
          <div>
            <h2>Mapa</h2>
            <div class="muted" id="map-meta">Carregando areas...</div>
          </div>
          <span class="pill" id="auto-refresh-pill">Atualizacao automatica a cada 60s</span>
        </div>
        <div id="map"></div>
      </div>
    </section>

    <section class="grid">
      <div class="panel">
        <div class="list-head">
          <div>
            <h2>Areas cadastradas</h2>
            <div class="muted" id="list-meta">Carregando...</div>
          </div>
          <span class="pill" id="visible-filter-pill">Filtro: Manual</span>
        </div>
        <table>
          <thead>
            <tr>
              <th>Area</th>
              <th>Modo</th>
              <th>Agencia</th>
              <th>Relevancia</th>
              <th>Pontos</th>
              <th>Atualizado</th>
              <th>Acoes</th>
            </tr>
          </thead>
          <tbody id="areas-body"></tbody>
        </table>
      </div>

      <div class="panel">
        <div class="editor-head">
          <div>
            <h2 id="editor-title">Cadastro manual</h2>
            <div class="muted" id="editor-subtitle">Mesma manutencao atual dos polygons em JSON.</div>
          </div>
          <span class="pill" id="editor-pill">Modo ativo: Manual</span>
        </div>

        <div class="form-panel active" id="manual-panel">
          <form id="manual-form">
            <div class="form-grid">
              <div>
                <label for="manual-name">Nome</label>
                <input id="manual-name" required />
              </div>
              <div>
                <label for="manual-slug">Slug</label>
                <input id="manual-slug" required pattern="^[a-z0-9_]+$" />
              </div>
            </div>
            <div class="form-grid triple">
              <div>
                <label for="manual-agencia">Agencia</label>
                <input id="manual-agencia" required />
              </div>
              <div>
                <label for="manual-relevancia">Relevancia (1-10)</label>
                <input id="manual-relevancia" type="number" min="1" max="10" required />
              </div>
              <div class="color-field">
                <label for="manual-color">Cor</label>
                <input id="manual-color" class="color-picker" type="color" value="#0b7285" />
              </div>
            </div>
            <div class="form-grid full">
              <div>
                <label for="manual-polygons">Polygons (JSON array ou GeoJSON FeatureCollection)</label>
                <textarea id="manual-polygons" required>[{"type":"Polygon","coordinates":[[[-46.64,-23.55],[-46.62,-23.55],[-46.62,-23.56],[-46.64,-23.56],[-46.64,-23.55]]]}]</textarea>
              </div>
            </div>
            <div class="row-actions" style="margin-top:10px;">
              <button class="primary" type="submit">Salvar manual</button>
              <button type="button" id="manual-preview-btn">Preview no mapa</button>
              <button type="button" id="manual-reset-btn">Limpar</button>
            </div>
          </form>
          <div class="note-box">
            O modo manual continua aceitando JSON array de polygons ou FeatureCollection GeoJSON.
          </div>
        </div>

        <div class="form-panel" id="automatic-panel">
          <form id="automatic-form">
            <div class="form-grid">
              <div>
                <label for="automatic-name">Nome</label>
                <input id="automatic-name" required />
              </div>
              <div>
                <label for="automatic-slug">Slug</label>
                <input id="automatic-slug" required pattern="^[a-z0-9_]+$" />
              </div>
            </div>
            <div class="form-grid triple">
              <div>
                <label for="automatic-agencia">Agencia</label>
                <input id="automatic-agencia" required />
              </div>
              <div>
                <label for="automatic-relevancia">Relevancia (1-10)</label>
                <input id="automatic-relevancia" type="number" min="1" max="10" required />
              </div>
              <div class="color-field">
                <label for="automatic-color">Cor</label>
                <input id="automatic-color" class="color-picker" type="color" value="#0b7285" />
              </div>
            </div>
            <div class="form-grid">
              <div>
                <label for="automatic-source-kind">Origem do arquivo</label>
                <select id="automatic-source-kind">
                  <option value="kml_upload">Arquivo KML/KMZ</option>
                  <option value="network_link">KML/KMZ de Network Link</option>
                </select>
              </div>
              <div id="refresh-interval-wrapper">
                <label for="automatic-refresh-interval">Refresh do link de rede (segundos)</label>
                <input id="automatic-refresh-interval" type="number" min="30" step="30" value="300" />
              </div>
            </div>
            <div class="form-grid full">
              <div>
                <label for="automatic-file">Arquivo KML/KMZ</label>
                <input id="automatic-file" type="file" accept=".kml,.kmz,application/vnd.google-earth.kml+xml,application/vnd.google-earth.kmz" />
              </div>
            </div>
            <div class="note-box" id="automatic-source-summary">
              Anexe um KML/KMZ para ler os polygons. Se selecionar Network Link, a API salva a URL remota e passa a atualizar o mapa automaticamente.
            </div>
            <div class="row-actions" style="margin-top:10px;">
              <button class="primary" type="submit">Salvar automatico</button>
              <button type="button" id="automatic-preview-btn">Ler arquivo</button>
              <button type="button" class="warning" id="automatic-refresh-btn">Atualizar agora</button>
              <button type="button" id="automatic-reset-btn">Limpar</button>
            </div>
          </form>
        </div>

        <div class="status" id="status"></div>

        <div class="section-title">
          <h3>Area selecionada (JSON)</h3>
          <span class="pill" id="selection-pill">Nenhuma area selecionada</span>
        </div>
        <pre id="area-json">Selecione uma area para visualizar os polygons.</pre>
      </div>
    </section>
  </div>
  <script
    src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"
    integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo="
    crossorigin=""
  ></script>
  <script>
    const apiBase = "/api/v1/areas";
    const state = {
      activeMode: "manual",
      editingSlug: null,
      editingMode: null,
      selectedSlug: null,
      areas: [],
      previewLayer: null,
      mapRenderToken: 0,
    };

    const DEFAULT_MANUAL_POLYGONS = '[{"type":"Polygon","coordinates":[[[-46.64,-23.55],[-46.62,-23.55],[-46.62,-23.56],[-46.64,-23.56],[-46.64,-23.55]]]}]';

    const map = L.map("map", { zoomControl: true }).setView([-23.55, -46.63], 11);
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 19,
      attribution: "&copy; OpenStreetMap contributors",
    }).addTo(map);

    const areaLayerGroup = L.featureGroup().addTo(map);
    const areaLayersBySlug = new Map();

    const els = {
      body: document.getElementById("areas-body"),
      listMeta: document.getElementById("list-meta"),
      mapMeta: document.getElementById("map-meta"),
      modeNote: document.getElementById("mode-note"),
      visibleFilterPill: document.getElementById("visible-filter-pill"),
      metricVisible: document.getElementById("metric-visible"),
      metricTotal: document.getElementById("metric-total"),
      metricAutomatic: document.getElementById("metric-automatic"),
      editorTitle: document.getElementById("editor-title"),
      editorSubtitle: document.getElementById("editor-subtitle"),
      editorPill: document.getElementById("editor-pill"),
      manualPanel: document.getElementById("manual-panel"),
      automaticPanel: document.getElementById("automatic-panel"),
      manualTab: document.getElementById("tab-manual"),
      automaticTab: document.getElementById("tab-automatic"),
      status: document.getElementById("status"),
      areaJson: document.getElementById("area-json"),
      selectionPill: document.getElementById("selection-pill"),
      manualForm: document.getElementById("manual-form"),
      manualName: document.getElementById("manual-name"),
      manualSlug: document.getElementById("manual-slug"),
      manualAgencia: document.getElementById("manual-agencia"),
      manualRelevancia: document.getElementById("manual-relevancia"),
      manualColor: document.getElementById("manual-color"),
      manualPolygons: document.getElementById("manual-polygons"),
      manualPreviewBtn: document.getElementById("manual-preview-btn"),
      manualResetBtn: document.getElementById("manual-reset-btn"),
      automaticForm: document.getElementById("automatic-form"),
      automaticName: document.getElementById("automatic-name"),
      automaticSlug: document.getElementById("automatic-slug"),
      automaticAgencia: document.getElementById("automatic-agencia"),
      automaticRelevancia: document.getElementById("automatic-relevancia"),
      automaticColor: document.getElementById("automatic-color"),
      automaticSourceKind: document.getElementById("automatic-source-kind"),
      automaticRefreshInterval: document.getElementById("automatic-refresh-interval"),
      refreshIntervalWrapper: document.getElementById("refresh-interval-wrapper"),
      automaticFile: document.getElementById("automatic-file"),
      automaticSourceSummary: document.getElementById("automatic-source-summary"),
      automaticPreviewBtn: document.getElementById("automatic-preview-btn"),
      automaticRefreshBtn: document.getElementById("automatic-refresh-btn"),
      automaticResetBtn: document.getElementById("automatic-reset-btn"),
    };

    function escapeHtml(value) {
      return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#39;");
    }

    function setStatus(message, isError = false) {
      els.status.textContent = message;
      els.status.style.color = isError ? "#b42318" : "#12703d";
    }

    function slugify(value) {
      return String(value || "")
        .normalize("NFD")
        .replace(/[\\u0300-\\u036f]/g, "")
        .toLowerCase()
        .replace(/[^a-z0-9]+/g, "_")
        .replace(/^_+|_+$/g, "")
        .replace(/_{2,}/g, "_");
    }

    function modeLabel(mode) {
      return mode === "automatic" ? "Automatico" : "Manual";
    }

    function humanDate(value) {
      if (!value) return "-";
      const parsed = new Date(value);
      if (Number.isNaN(parsed.getTime())) return value;
      return parsed.toLocaleString("pt-BR");
    }

    function getVisibleAreas() {
      return state.areas.filter((area) => (area.mode || "manual") === state.activeMode);
    }

    function updateMetrics() {
      const automaticCount = state.areas.filter((area) => (area.mode || "manual") === "automatic").length;
      els.metricVisible.textContent = String(getVisibleAreas().length);
      els.metricTotal.textContent = String(state.areas.length);
      els.metricAutomatic.textContent = String(automaticCount);
      els.visibleFilterPill.textContent = `Filtro: ${modeLabel(state.activeMode)}`;
      els.editorPill.textContent = `Modo ativo: ${modeLabel(state.activeMode)}`;
      els.mapMeta.textContent = `${getVisibleAreas().length} area(s) visiveis no mapa de ${modeLabel(state.activeMode).toLowerCase()}.`;
      if (state.activeMode === "automatic") {
        els.modeNote.textContent = "No modo automatico, a API interpreta KML/KMZ, suporta arquivos com NetworkLink e mantem os polygons atualizados pelo object store.";
        els.editorTitle.textContent = "Cadastro automatico";
        els.editorSubtitle.textContent = "Upload de KML/KMZ com refresh automatico para arquivos de Network Link.";
      } else {
        els.modeNote.textContent = "No modo manual, o fluxo continua igual ao atual: polygons em JSON, preview local e CRUD direto.";
        els.editorTitle.textContent = "Cadastro manual";
        els.editorSubtitle.textContent = "Mesma manutencao atual dos polygons em JSON.";
      }
    }

    function colorFromSlug(slug) {
      let hash = 0;
      for (let i = 0; i < slug.length; i++) hash = slug.charCodeAt(i) + ((hash << 5) - hash);
      const hue = Math.abs(hash) % 360;
      return hslToHex(hue, 70, 42);
    }

    function hslToHex(hue, saturation, lightness) {
      const s = saturation / 100;
      const l = lightness / 100;
      const chroma = (1 - Math.abs(2 * l - 1)) * s;
      const hueSection = (hue / 60) % 6;
      const x = chroma * (1 - Math.abs((hueSection % 2) - 1));
      let r1 = 0;
      let g1 = 0;
      let b1 = 0;

      if (hueSection >= 0 && hueSection < 1) [r1, g1, b1] = [chroma, x, 0];
      else if (hueSection < 2) [r1, g1, b1] = [x, chroma, 0];
      else if (hueSection < 3) [r1, g1, b1] = [0, chroma, x];
      else if (hueSection < 4) [r1, g1, b1] = [0, x, chroma];
      else if (hueSection < 5) [r1, g1, b1] = [x, 0, chroma];
      else [r1, g1, b1] = [chroma, 0, x];

      const match = l - chroma / 2;
      const toHex = (value) => Math.round((value + match) * 255).toString(16).padStart(2, "0");
      return `#${toHex(r1)}${toHex(g1)}${toHex(b1)}`;
    }

    function normalizeColor(value, slug = "") {
      const normalized = String(value || "").trim().toLowerCase();
      if (/^#[0-9a-f]{6}$/.test(normalized)) return normalized;
      return colorFromSlug(slug || "area");
    }

    function polygonsToLeafletLatLngs(polygons) {
      if (!Array.isArray(polygons)) {
        throw new Error("Formato invalido para polygons: esperado array.");
      }
      return polygons.map((polygon) => {
        const rings = polygon.coordinates || [];
        return rings.map((ring) => ring.map((coord) => [coord[1], coord[0]]));
      });
    }

    function normalizePolygonsInput(rawInput) {
      if (Array.isArray(rawInput)) return rawInput;

      if (rawInput && Array.isArray(rawInput.polygons)) {
        return rawInput.polygons;
      }

      if (rawInput && rawInput.type === "Polygon" && Array.isArray(rawInput.coordinates)) {
        return [{
          type: "Polygon",
          coordinates: rawInput.coordinates,
        }];
      }

      if (rawInput && rawInput.type === "MultiPolygon" && Array.isArray(rawInput.coordinates)) {
        return rawInput.coordinates.map((coordinates) => ({
          type: "Polygon",
          coordinates,
        }));
      }

      if (rawInput && rawInput.type === "Feature") {
        return normalizePolygonsInput({
          type: "FeatureCollection",
          features: [rawInput],
        });
      }

      if (rawInput && rawInput.type === "FeatureCollection" && Array.isArray(rawInput.features)) {
        const polygons = [];
        for (const feature of rawInput.features) {
          const geometry = feature && feature.geometry;
          if (!geometry || !geometry.type || !geometry.coordinates) continue;
          if (geometry.type === "Polygon") {
            polygons.push({ type: "Polygon", coordinates: geometry.coordinates });
          }
          if (geometry.type === "MultiPolygon") {
            for (const coordinates of geometry.coordinates) {
              polygons.push({ type: "Polygon", coordinates });
            }
          }
        }
        if (!polygons.length) {
          throw new Error("GeoJSON sem geometrias do tipo Polygon/MultiPolygon.");
        }
        return polygons;
      }

      throw new Error("Formato invalido. Use JSON array de polygons ou FeatureCollection GeoJSON.");
    }

    function validatePolygonsForApi(polygons) {
      if (!Array.isArray(polygons) || !polygons.length) {
        throw new Error("Informe ao menos um Polygon valido.");
      }

      polygons.forEach((polygon, polyIndex) => {
        if (!polygon || polygon.type !== "Polygon" || !Array.isArray(polygon.coordinates)) {
          throw new Error(`Polygon ${polyIndex + 1} invalido.`);
        }
        if (!polygon.coordinates.length) {
          throw new Error(`Polygon ${polyIndex + 1} sem aneis.`);
        }
        polygon.coordinates.forEach((ring, ringIndex) => {
          if (!Array.isArray(ring) || ring.length < 4) {
            throw new Error(`Polygon ${polyIndex + 1}, anel ${ringIndex + 1} precisa de ao menos 4 pontos.`);
          }
        });
      });
    }

    function parseManualPolygonsFromInput(isPreview = false) {
      let parsed;
      try {
        parsed = JSON.parse(els.manualPolygons.value);
      } catch (error) {
        throw new Error(isPreview ? "JSON invalido para preview." : "JSON de polygons invalido.");
      }
      const polygons = normalizePolygonsInput(parsed);
      validatePolygonsForApi(polygons);
      return polygons;
    }

    function extractApiErrorMessage(err) {
      if (!err || !err.detail) return "Falha ao processar a requisicao.";
      if (typeof err.detail === "string") return err.detail;
      if (Array.isArray(err.detail)) {
        return err.detail
          .map((item) => {
            const loc = Array.isArray(item?.loc) ? item.loc.join(".") : "";
            const msg = item?.msg || "";
            return loc ? `${loc}: ${msg}` : msg;
          })
          .filter(Boolean)
          .join(" | ");
      }
      return "Falha ao processar a requisicao.";
    }

    function removePreviewLayer() {
      if (state.previewLayer) {
        map.removeLayer(state.previewLayer);
        state.previewLayer = null;
      }
    }

    function highlightSelectedArea() {
      areaLayersBySlug.forEach((entry, slug) => {
        const baseColor = entry.color;
        const isSelected = slug === state.selectedSlug;
        entry.layer.setStyle({
          color: baseColor,
          weight: isSelected ? 4 : 2,
          fillOpacity: isSelected ? 0.36 : 0.18,
        });
        if (isSelected) entry.layer.bringToFront();
      });
    }

    function drawPreviewPolygons(polygons, message, color = "#38bdf8") {
      removePreviewLayer();
      const latLngPolygons = polygonsToLeafletLatLngs(polygons);
      const layers = latLngPolygons.map((latLngRings) =>
        L.polygon(latLngRings, {
          color: "#0f172a",
          weight: 2,
          fillColor: color,
          fillOpacity: 0.22,
          dashArray: "7 5",
        })
      );
      state.previewLayer = L.featureGroup(layers).addTo(map);
      const bounds = state.previewLayer.getBounds();
      if (bounds.isValid()) map.fitBounds(bounds.pad(0.2));
      setStatus(message || "Preview aplicado no mapa.");
    }

    function drawAreaOnMap(area) {
      const color = normalizeColor(area.color, area.slug);
      let latLngPolygons;
      try {
        latLngPolygons = polygonsToLeafletLatLngs(area.polygons || []);
      } catch (error) {
        return;
      }

      const layers = latLngPolygons.map((latLngRings) =>
        L.polygon(latLngRings, {
          color,
          weight: 2,
          fillColor: color,
          fillOpacity: 0.18,
        })
      );

      const layer = L.featureGroup(layers);
      const badge = area.mode === "automatic" ? "Automatico" : "Manual";
      layer.bindPopup(`<strong>${escapeHtml(area.name)}</strong><br/>${escapeHtml(area.slug)}<br/>${escapeHtml(badge)}`);
      layer.on("click", () => {
        state.selectedSlug = area.slug;
        highlightSelectedArea();
        viewArea(area.slug);
      });
      areaLayerGroup.addLayer(layer);
      areaLayersBySlug.set(area.slug, { layer, color });
    }

    async function fitMapToAllAreas() {
      if (!areaLayerGroup.getLayers().length) return;
      const bounds = areaLayerGroup.getBounds();
      if (bounds.isValid()) map.fitBounds(bounds.pad(0.12));
    }

    function renderModeTabs() {
      els.manualTab.classList.toggle("active", state.activeMode === "manual");
      els.automaticTab.classList.toggle("active", state.activeMode === "automatic");
      els.manualPanel.classList.toggle("active", state.activeMode === "manual");
      els.automaticPanel.classList.toggle("active", state.activeMode === "automatic");
      updateMetrics();
    }

    function renderAutomaticSourceSummary(automaticSource, extraLabel = "") {
      if (!automaticSource) {
        els.automaticSourceSummary.textContent = "Anexe um KML/KMZ para ler os polygons. Se selecionar Network Link, a API salva a URL remota e passa a atualizar o mapa automaticamente.";
        return;
      }

      const lines = [];
      if (extraLabel) lines.push(`<strong>${escapeHtml(extraLabel)}</strong>`);
      lines.push(`Tipo: ${escapeHtml(automaticSource.type === "network_link" ? "NetworkLink" : "Arquivo KML/KMZ")}`);
      if (automaticSource.source_file_name) lines.push(`Arquivo: ${escapeHtml(automaticSource.source_file_name)}`);
      if (automaticSource.link_name) lines.push(`Link encontrado: ${escapeHtml(automaticSource.link_name)}`);
      if (automaticSource.source_url) lines.push(`URL remota: ${escapeHtml(automaticSource.source_url)}`);
      if (automaticSource.resolved_document_name) lines.push(`Documento efetivo: ${escapeHtml(automaticSource.resolved_document_name)}`);
      if (automaticSource.refresh_interval_seconds) lines.push(`Refresh: ${escapeHtml(automaticSource.refresh_interval_seconds)}s`);
      if (automaticSource.last_refreshed_at) lines.push(`Ultimo refresh: ${escapeHtml(humanDate(automaticSource.last_refreshed_at))}`);
      if (automaticSource.last_refresh_error) lines.push(`Ultimo erro: ${escapeHtml(automaticSource.last_refresh_error)}`);
      els.automaticSourceSummary.innerHTML = lines.join("<br/>");
    }

    function resetManualForm() {
      if (state.editingMode === "manual") {
        state.editingSlug = null;
        state.editingMode = null;
      }
      els.manualForm.reset();
      els.manualRelevancia.value = 1;
      els.manualColor.value = "#0b7285";
      els.manualPolygons.value = DEFAULT_MANUAL_POLYGONS;
      removePreviewLayer();
      if (state.activeMode === "manual") {
        setStatus("");
      }
    }

    function resetAutomaticForm() {
      if (state.editingMode === "automatic") {
        state.editingSlug = null;
        state.editingMode = null;
      }
      els.automaticForm.reset();
      els.automaticRelevancia.value = 1;
      els.automaticColor.value = "#0b7285";
      els.automaticSourceKind.value = "kml_upload";
      els.automaticRefreshInterval.value = 300;
      toggleAutomaticRefreshInterval();
      renderAutomaticSourceSummary(null);
      removePreviewLayer();
      if (state.activeMode === "automatic") {
        setStatus("");
      }
    }

    function resetSelectionIfHidden() {
      const selectedSummary = state.areas.find((area) => area.slug === state.selectedSlug);
      if (!selectedSummary || (selectedSummary.mode || "manual") !== state.activeMode) {
        state.selectedSlug = null;
        els.selectionPill.textContent = "Nenhuma area selecionada";
        els.areaJson.textContent = "Selecione uma area para visualizar os polygons.";
      }
    }

    async function getAreaDetails(slug) {
      const res = await fetch(`${apiBase}/${slug}`);
      if (!res.ok) throw new Error(`Falha ao carregar area ${slug}.`);
      return res.json();
    }

    async function renderMapForActiveMode() {
      const visibleAreas = getVisibleAreas();
      const renderToken = ++state.mapRenderToken;

      areaLayerGroup.clearLayers();
      areaLayersBySlug.clear();

      if (!visibleAreas.length) return;

      const detailedAreas = await Promise.all(
        visibleAreas.map((area) => getAreaDetails(area.slug).catch(() => null))
      );
      if (renderToken !== state.mapRenderToken) return;

      detailedAreas.filter(Boolean).forEach(drawAreaOnMap);
      highlightSelectedArea();

      if (state.selectedSlug && areaLayersBySlug.has(state.selectedSlug)) {
        const entry = areaLayersBySlug.get(state.selectedSlug);
        const bounds = entry.layer.getBounds();
        if (bounds.isValid()) map.fitBounds(bounds.pad(0.2));
        return;
      }

      await fitMapToAllAreas();
    }

    function renderAreaList() {
      const visibleAreas = getVisibleAreas();
      els.listMeta.textContent = `${visibleAreas.length} area(s) em ${modeLabel(state.activeMode).toLowerCase()} de um total de ${state.areas.length}.`;

      if (!visibleAreas.length) {
        els.body.innerHTML = '<tr><td colspan="7" class="muted">Nenhuma area cadastrada neste modo.</td></tr>';
        return;
      }

      els.body.innerHTML = visibleAreas.map((area) => {
        const color = normalizeColor(area.color, area.slug);
        const refreshText = area.mode === "automatic"
          ? (area.last_refresh_error ? `Erro: ${escapeHtml(area.last_refresh_error)}` : escapeHtml(humanDate(area.last_refreshed_at)))
          : "-";
        const badgeClass = area.mode === "automatic" ? "automatic" : "manual";
        const refreshButton = area.mode === "automatic" && area.automatic_source_type === "network_link"
          ? `<button class="warning" onclick="refreshAutomaticArea('${area.slug}')">Atualizar</button>`
          : "";

        return `
          <tr>
            <td>
              <div class="name-cell">
                <div class="area-name-line">
                  <span class="color-dot" style="background:${escapeHtml(color)};"></span>
                  <strong>${escapeHtml(area.name)}</strong>
                </div>
                <span class="mini"><code>${escapeHtml(area.slug)}</code></span>
              </div>
            </td>
            <td><span class="badge ${badgeClass}">${escapeHtml(modeLabel(area.mode || "manual"))}</span></td>
            <td>
              <div class="name-cell">
                <span>${escapeHtml(area.agencia || "-")}</span>
                <span class="mini">${escapeHtml(color)}</span>
              </div>
            </td>
            <td>${escapeHtml(area.relevancia ?? "-")}</td>
            <td>
              <div class="name-cell">
                <span>${escapeHtml(area.total_points)}</span>
                <span class="mini">${escapeHtml(area.polygon_count)} polygon(s)</span>
              </div>
            </td>
            <td class="mini">${refreshText}</td>
            <td>
              <div class="row-actions">
                <button onclick="viewArea('${area.slug}')">Ver</button>
                <button onclick="focusAreaOnMap('${area.slug}')">Mapa</button>
                <button onclick="editArea('${area.slug}')">Editar</button>
                ${refreshButton}
                <button class="danger" onclick="deleteArea('${area.slug}')">Excluir</button>
              </div>
            </td>
          </tr>
        `;
      }).join("");
    }

    async function loadAreas(options = {}) {
      const { silent = false, preserveStatus = false } = options;

      try {
        const res = await fetch(apiBase);
        if (!res.ok) throw new Error("Falha ao carregar areas.");
        state.areas = await res.json();
        resetSelectionIfHidden();
        renderModeTabs();
        renderAreaList();
        await renderMapForActiveMode();

        if (state.selectedSlug) {
          await viewArea(state.selectedSlug, true);
        }

        if (!silent && !preserveStatus && !els.status.textContent) {
          setStatus("");
        }
      } catch (error) {
        els.listMeta.textContent = "Erro ao carregar.";
        setStatus(error.message || "Erro inesperado.", true);
      }
    }

    async function viewArea(slug, preserveStatus = false) {
      try {
        const data = await getAreaDetails(slug);
        state.selectedSlug = slug;
        const areaMode = data.mode || "manual";
        if (areaMode !== state.activeMode) {
          state.activeMode = areaMode;
          renderModeTabs();
          renderAreaList();
          await renderMapForActiveMode();
        }
        els.areaJson.textContent = JSON.stringify(data, null, 2);
        els.selectionPill.textContent = `${data.name} (${modeLabel(areaMode)})`;
        highlightSelectedArea();

        const layerEntry = areaLayersBySlug.get(slug);
        if (layerEntry) {
          const bounds = layerEntry.layer.getBounds();
          if (bounds.isValid()) map.fitBounds(bounds.pad(0.2));
        }

        if (!preserveStatus) {
          setStatus(`Area '${slug}' carregada.`);
        }
      } catch (error) {
        setStatus(error.message || "Nao foi possivel carregar a area.", true);
      }
    }

    async function focusAreaOnMap(slug) {
      const summary = state.areas.find((area) => area.slug === slug);
      if (!summary) return;

      if ((summary.mode || "manual") !== state.activeMode) {
        state.activeMode = summary.mode || "manual";
        renderModeTabs();
        renderAreaList();
        await renderMapForActiveMode();
      }

      state.selectedSlug = slug;
      highlightSelectedArea();
      const entry = areaLayersBySlug.get(slug);
      if (!entry) return;
      const bounds = entry.layer.getBounds();
      if (bounds.isValid()) map.fitBounds(bounds.pad(0.2));
      entry.layer.openPopup();
      await viewArea(slug, true);
    }

    async function editArea(slug) {
      try {
        const data = await getAreaDetails(slug);
        state.editingSlug = slug;
        state.editingMode = data.mode || "manual";
        state.selectedSlug = slug;
        els.areaJson.textContent = JSON.stringify(data, null, 2);
        els.selectionPill.textContent = `${data.name} (${modeLabel(data.mode || "manual")})`;

        if ((data.mode || "manual") === "automatic") {
          state.activeMode = "automatic";
          renderModeTabs();
          els.automaticName.value = data.name || "";
          els.automaticSlug.value = data.slug || "";
          els.automaticAgencia.value = data.agencia || "";
          els.automaticRelevancia.value = data.relevancia || 1;
          els.automaticColor.value = normalizeColor(data.color, data.slug || slug);
          els.automaticSourceKind.value = data.automatic_source?.type || "kml_upload";
          els.automaticRefreshInterval.value = data.automatic_source?.refresh_interval_seconds || 300;
          toggleAutomaticRefreshInterval();
          renderAutomaticSourceSummary(data.automatic_source, "Fonte atualmente salva");
          setStatus("Modo edicao automatico ativado.");
        } else {
          state.activeMode = "manual";
          renderModeTabs();
          els.manualName.value = data.name || "";
          els.manualSlug.value = data.slug || "";
          els.manualAgencia.value = data.agencia || "";
          els.manualRelevancia.value = data.relevancia || 1;
          els.manualColor.value = normalizeColor(data.color, data.slug || slug);
          els.manualPolygons.value = JSON.stringify(data.polygons || [], null, 2);
          setStatus("Modo edicao manual ativado.");
        }

        renderAreaList();
        await renderMapForActiveMode();
        highlightSelectedArea();
      } catch (error) {
        setStatus(error.message || "Nao foi possivel carregar a area para edicao.", true);
      }
    }

    async function deleteArea(slug) {
      const ok = confirm(`Excluir a area '${slug}'?`);
      if (!ok) return;

      const res = await fetch(`${apiBase}/${slug}`, { method: "DELETE" });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        setStatus(extractApiErrorMessage(err), true);
        return;
      }

      if (state.editingSlug === slug) {
        state.editingMode = null;
        resetManualForm();
        resetAutomaticForm();
      }
      if (state.selectedSlug === slug) {
        state.selectedSlug = null;
        els.selectionPill.textContent = "Nenhuma area selecionada";
        els.areaJson.textContent = "Selecione uma area para visualizar os polygons.";
      }

      setStatus(`Area '${slug}' removida.`);
      await loadAreas({ silent: true, preserveStatus: true });
    }

    function previewManualPolygons() {
      try {
        const polygons = parseManualPolygonsFromInput(true);
        drawPreviewPolygons(
          polygons,
          "Preview manual aplicado no mapa.",
          normalizeColor(els.manualColor.value, els.manualSlug.value.trim())
        );
      } catch (error) {
        setStatus(error.message || "Falha no preview dos polygons.", true);
      }
    }

    async function saveManualArea(event) {
      event.preventDefault();
      removePreviewLayer();

      let polygons;
      try {
        polygons = parseManualPolygonsFromInput(false);
      } catch (error) {
        setStatus(error.message || "Falha ao ler polygons.", true);
        return;
      }

      const payload = {
        name: els.manualName.value.trim(),
        slug: els.manualSlug.value.trim(),
        agencia: els.manualAgencia.value.trim(),
        relevancia: Number(els.manualRelevancia.value),
        color: normalizeColor(els.manualColor.value, els.manualSlug.value.trim()),
        polygons,
        mode: "manual",
      };

      const isEditing = state.editingMode === "manual" && !!state.editingSlug;
      const method = isEditing ? "PATCH" : "POST";
      const url = isEditing ? `${apiBase}/${state.editingSlug}` : apiBase;

      const res = await fetch(url, {
        method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        setStatus(extractApiErrorMessage(err), true);
        return;
      }

      state.editingSlug = payload.slug;
      state.editingMode = "manual";
      state.selectedSlug = payload.slug;
      setStatus(isEditing ? "Area manual atualizada com sucesso." : "Area manual salva com sucesso.");
      await loadAreas({ silent: true, preserveStatus: true });
      await viewArea(payload.slug, true);
    }

    function buildAutomaticFormData() {
      const formData = new FormData();
      formData.append("name", els.automaticName.value.trim());
      formData.append("slug", els.automaticSlug.value.trim());
      formData.append("agencia", els.automaticAgencia.value.trim());
      formData.append("relevancia", String(Number(els.automaticRelevancia.value)));
      formData.append("color", normalizeColor(els.automaticColor.value, els.automaticSlug.value.trim()));
      formData.append("source_kind", els.automaticSourceKind.value);
      if (els.automaticSourceKind.value === "network_link") {
        formData.append("refresh_interval_seconds", String(Number(els.automaticRefreshInterval.value || 300)));
      }
      if (state.editingMode === "automatic" && state.editingSlug) {
        formData.append("editing_slug", state.editingSlug);
      }
      return formData;
    }

    async function previewAutomaticArea() {
      removePreviewLayer();
      const file = els.automaticFile.files[0];
      if (!file) {
        setStatus("Selecione um arquivo KML/KMZ para leitura.", true);
        return;
      }

      const formData = new FormData();
      formData.append("source_kind", els.automaticSourceKind.value);
      if (els.automaticSourceKind.value === "network_link") {
        formData.append("refresh_interval_seconds", String(Number(els.automaticRefreshInterval.value || 300)));
      }
      formData.append("file", file);

      const res = await fetch(`${apiBase}/automatic/preview`, {
        method: "POST",
        body: formData,
      });

      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        setStatus(extractApiErrorMessage(data), true);
        return;
      }

      try {
        drawPreviewPolygons(
          data.polygons || [],
          "Arquivo automatico lido com sucesso.",
          normalizeColor(els.automaticColor.value, els.automaticSlug.value.trim())
        );
      } catch (error) {
        setStatus(error.message || "Nao foi possivel desenhar o preview automatico.", true);
        return;
      }

      if (!els.automaticName.value.trim() && data.document_name) {
        els.automaticName.value = data.document_name;
      }
      if (!els.automaticSlug.value.trim() && data.document_name) {
        els.automaticSlug.value = slugify(data.document_name);
      }
      renderAutomaticSourceSummary(data.automatic_source, "Preview da fonte");
    }

    async function saveAutomaticArea(event) {
      event.preventDefault();
      removePreviewLayer();

      const file = els.automaticFile.files[0];
      const isEditing = state.editingMode === "automatic" && !!state.editingSlug;

      if (!isEditing && !file) {
        setStatus("Selecione um arquivo KML/KMZ para salvar a area automatica.", true);
        return;
      }

      if (file) {
        const formData = buildAutomaticFormData();
        formData.append("file", file);

        const res = await fetch(`${apiBase}/automatic`, {
          method: "POST",
          body: formData,
        });

        const data = await res.json().catch(() => ({}));
        if (!res.ok) {
          setStatus(extractApiErrorMessage(data), true);
          return;
        }

        const targetSlug = els.automaticSlug.value.trim();
        state.editingSlug = targetSlug;
        state.editingMode = "automatic";
        state.selectedSlug = targetSlug;
        renderAutomaticSourceSummary(data.area?.automatic_source, "Fonte salva");
        setStatus(isEditing ? "Area automatica atualizada com sucesso." : "Area automatica salva com sucesso.");
        await loadAreas({ silent: true, preserveStatus: true });
        await viewArea(targetSlug, true);
        return;
      }

      const current = await getAreaDetails(state.editingSlug).catch(() => null);
      if (!current) {
        setStatus("Nao foi possivel carregar a area automatica para atualizar.", true);
        return;
      }

      const currentSource = current.automatic_source || {};
      const requestedSourceKind = els.automaticSourceKind.value;
      if ((currentSource.type || "kml_upload") !== requestedSourceKind) {
        setStatus("Para trocar o tipo de origem automatica, envie um novo arquivo.", true);
        return;
      }

      const automaticSource = {
        ...currentSource,
        refresh_interval_seconds: requestedSourceKind === "network_link"
          ? Number(els.automaticRefreshInterval.value || currentSource.refresh_interval_seconds || 300)
          : null,
      };

      const payload = {
        name: els.automaticName.value.trim(),
        slug: els.automaticSlug.value.trim(),
        agencia: els.automaticAgencia.value.trim(),
        relevancia: Number(els.automaticRelevancia.value),
        color: normalizeColor(els.automaticColor.value, els.automaticSlug.value.trim()),
        mode: "automatic",
        automatic_source: automaticSource,
      };

      const res = await fetch(`${apiBase}/${state.editingSlug}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        setStatus(extractApiErrorMessage(data), true);
        return;
      }

      state.editingSlug = payload.slug;
      state.editingMode = "automatic";
      state.selectedSlug = payload.slug;
      renderAutomaticSourceSummary(data.area?.automatic_source || automaticSource, "Fonte salva");
      setStatus("Metadados da area automatica atualizados com sucesso.");
      await loadAreas({ silent: true, preserveStatus: true });
      await viewArea(payload.slug, true);
    }

    async function refreshAutomaticArea(slug = null) {
      const targetSlug = slug || (state.editingMode === "automatic" ? state.editingSlug : null) || state.selectedSlug;
      if (!targetSlug) {
        setStatus("Selecione uma area automatica para forcar refresh.", true);
        return;
      }

      const res = await fetch(`${apiBase}/${targetSlug}/refresh`, { method: "POST" });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        setStatus(extractApiErrorMessage(data), true);
        return;
      }

      if (data.area?.automatic_source) {
        renderAutomaticSourceSummary(data.area.automatic_source, "Refresh executado");
      }
      state.selectedSlug = targetSlug;
      setStatus(`Refresh concluido para '${targetSlug}'.`);
      await loadAreas({ silent: true, preserveStatus: true });
      await viewArea(targetSlug, true);
    }

    function toggleAutomaticRefreshInterval() {
      const isNetworkLink = els.automaticSourceKind.value === "network_link";
      els.refreshIntervalWrapper.classList.toggle("hidden", !isNetworkLink);
    }

    function activateMode(mode) {
      state.activeMode = mode;
      renderModeTabs();
      renderAreaList();
      renderMapForActiveMode();
      if (mode === "manual") {
        setStatus("Modo manual ativo.");
      } else {
        setStatus("Modo automatico ativo.");
      }
    }

    function wireAutoSlug(inputEl, slugEl) {
      inputEl.addEventListener("input", () => {
        if (!slugEl.value.trim() || slugEl.dataset.autofill === "true") {
          slugEl.value = slugify(inputEl.value);
          slugEl.dataset.autofill = "true";
        }
      });
      slugEl.addEventListener("input", () => {
        slugEl.dataset.autofill = "false";
      });
    }

    els.manualForm.addEventListener("submit", saveManualArea);
    els.manualPreviewBtn.addEventListener("click", previewManualPolygons);
    els.manualResetBtn.addEventListener("click", resetManualForm);
    els.automaticForm.addEventListener("submit", saveAutomaticArea);
    els.automaticPreviewBtn.addEventListener("click", previewAutomaticArea);
    els.automaticRefreshBtn.addEventListener("click", () => refreshAutomaticArea());
    els.automaticResetBtn.addEventListener("click", resetAutomaticForm);
    els.automaticSourceKind.addEventListener("change", toggleAutomaticRefreshInterval);
    els.manualTab.addEventListener("click", () => activateMode("manual"));
    els.automaticTab.addEventListener("click", () => activateMode("automatic"));

    wireAutoSlug(els.manualName, els.manualSlug);
    wireAutoSlug(els.automaticName, els.automaticSlug);

    resetManualForm();
    resetAutomaticForm();
    renderModeTabs();
    loadAreas();
    setInterval(() => {
      loadAreas({ silent: true, preserveStatus: true });
    }, 60000);

    window.viewArea = viewArea;
    window.focusAreaOnMap = focusAreaOnMap;
    window.editArea = editArea;
    window.deleteArea = deleteArea;
    window.refreshAutomaticArea = refreshAutomaticArea;
  </script>
</body>
</html>
"""
