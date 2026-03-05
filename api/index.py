"""
Entrypoint Vercel - expoe a variavel `app` (FastAPI/ASGI).
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

from lib.models import (
    AnalysisRequest,
    AnalysisResponse,
    AreaInput,
    AreaPatchInput,
    AreaSummary,
)
from lib.geo_service import analyze
from lib.areas_repository import repository

app = FastAPI(
    title="Geo Analysis API",
    description=(
        "Verifica se um ponto esta dentro de areas geograficas "
        "e calcula a distancia ate a borda mais proxima."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

FRONTEND_HTML = """
<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Score API - Areas</title>
  <style>
    :root {
      --bg: #f4f6f8;
      --panel: #ffffff;
      --text: #1f2933;
      --subtle: #52606d;
      --border: #d9e2ec;
      --primary: #0b7285;
      --danger: #c92a2a;
      --radius: 10px;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: "Segoe UI", Tahoma, sans-serif;
      color: var(--text);
      background: linear-gradient(180deg, #eef4f7 0%, var(--bg) 100%);
    }
    .container {
      max-width: 1100px;
      margin: 0 auto;
      padding: 24px 16px 40px;
    }
    h1, h2, h3 { margin: 0 0 12px; }
    .grid {
      display: grid;
      gap: 16px;
      grid-template-columns: 1.2fr 1fr;
    }
    .panel {
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 16px;
      box-shadow: 0 8px 20px rgba(15, 23, 42, 0.06);
    }
    table {
      width: 100%;
      border-collapse: collapse;
      font-size: 14px;
    }
    th, td {
      text-align: left;
      padding: 10px 8px;
      border-bottom: 1px solid var(--border);
      vertical-align: top;
    }
    th { color: var(--subtle); font-weight: 600; }
    .row-actions {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
    }
    button {
      border: 0;
      border-radius: 8px;
      padding: 8px 10px;
      cursor: pointer;
      font-size: 13px;
      background: #e8eff3;
      color: #123;
    }
    button.primary { background: var(--primary); color: #fff; }
    button.danger { background: var(--danger); color: #fff; }
    .form-row {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 10px;
      margin-bottom: 10px;
    }
    .form-row.full { grid-template-columns: 1fr; }
    label { font-size: 12px; color: var(--subtle); margin-bottom: 4px; display: block; }
    input, textarea {
      width: 100%;
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 9px 10px;
      font-size: 14px;
      font-family: inherit;
    }
    textarea { min-height: 140px; resize: vertical; }
    .muted { color: var(--subtle); font-size: 13px; }
    .status { margin-top: 8px; min-height: 18px; font-size: 13px; }
    pre {
      background: #0f172a;
      color: #dbeafe;
      border-radius: 8px;
      padding: 12px;
      overflow: auto;
      max-height: 320px;
      font-size: 12px;
    }
    @media (max-width: 900px) {
      .grid { grid-template-columns: 1fr; }
      .form-row { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <div class="container">
    <h1>Gestao de Areas</h1>
    <p class="muted">CRUD simplificado de areas e visualizacao dos polygons em JSON.</p>
    <div class="grid">
      <section class="panel">
        <h2>Areas cadastradas</h2>
        <div class="muted" id="list-meta">Carregando...</div>
        <table>
          <thead>
            <tr>
              <th>Nome</th>
              <th>Slug</th>
              <th>Polygons</th>
              <th>Pontos</th>
              <th>Acoes</th>
            </tr>
          </thead>
          <tbody id="areas-body"></tbody>
        </table>
      </section>

      <section class="panel">
        <h2 id="form-title">Nova area</h2>
        <form id="area-form">
          <div class="form-row">
            <div>
              <label for="name">Nome</label>
              <input id="name" required />
            </div>
            <div>
              <label for="slug">Slug</label>
              <input id="slug" required pattern="^[a-z0-9_]+$" />
            </div>
          </div>
          <div class="form-row">
            <div>
              <label for="agencia">Agencia</label>
              <input id="agencia" required />
            </div>
            <div>
              <label for="relevancia">Relevancia (1-10)</label>
              <input id="relevancia" type="number" min="1" max="10" required />
            </div>
          </div>
          <div class="form-row full">
            <div>
              <label for="polygons">Polygons (JSON array)</label>
              <textarea id="polygons" required>[{"type":"Polygon","coordinates":[[[-46.64,-23.55],[-46.62,-23.55],[-46.62,-23.56],[-46.64,-23.56],[-46.64,-23.55]]]}]</textarea>
            </div>
          </div>
          <div class="row-actions">
            <button class="primary" type="submit" id="save-btn">Salvar</button>
            <button type="button" id="reset-btn">Limpar</button>
          </div>
        </form>
        <div class="status" id="status"></div>
      </section>
    </div>

    <section class="panel" style="margin-top:16px;">
      <h3>Visualizacao da area selecionada</h3>
      <pre id="area-json">Selecione uma area para visualizar os polygons.</pre>
    </section>
  </div>

  <script>
    const apiBase = "/api/v1/areas";
    let editingSlug = null;

    const els = {
      body: document.getElementById("areas-body"),
      listMeta: document.getElementById("list-meta"),
      formTitle: document.getElementById("form-title"),
      form: document.getElementById("area-form"),
      name: document.getElementById("name"),
      slug: document.getElementById("slug"),
      agencia: document.getElementById("agencia"),
      relevancia: document.getElementById("relevancia"),
      polygons: document.getElementById("polygons"),
      status: document.getElementById("status"),
      areaJson: document.getElementById("area-json"),
      resetBtn: document.getElementById("reset-btn"),
    };

    function setStatus(message, isError = false) {
      els.status.textContent = message;
      els.status.style.color = isError ? "#b42318" : "#12703d";
    }

    function resetForm() {
      editingSlug = null;
      els.formTitle.textContent = "Nova area";
      els.form.reset();
      els.relevancia.value = 1;
      els.polygons.value = '[{"type":"Polygon","coordinates":[[[-46.64,-23.55],[-46.62,-23.55],[-46.62,-23.56],[-46.64,-23.56],[-46.64,-23.55]]]}]';
      els.areaJson.textContent = "Selecione uma area para visualizar os polygons.";
      setStatus("");
    }

    async function loadAreas() {
      const res = await fetch(apiBase);
      if (!res.ok) throw new Error("Falha ao carregar areas.");
      const areas = await res.json();
      els.listMeta.textContent = areas.length + " area(s)";

      if (!areas.length) {
        els.body.innerHTML = '<tr><td colspan="5" class="muted">Nenhuma area cadastrada.</td></tr>';
        return;
      }

      els.body.innerHTML = areas.map(area => `
        <tr>
          <td>${area.name}</td>
          <td><code>${area.slug}</code></td>
          <td>${area.polygon_count}</td>
          <td>${area.total_points}</td>
          <td>
            <div class="row-actions">
              <button onclick="viewArea('${area.slug}')">Ver</button>
              <button onclick="editArea('${area.slug}')">Editar</button>
              <button class="danger" onclick="deleteArea('${area.slug}')">Excluir</button>
            </div>
          </td>
        </tr>
      `).join("");
    }

    async function viewArea(slug) {
      const res = await fetch(`${apiBase}/${slug}`);
      const data = await res.json();
      els.areaJson.textContent = JSON.stringify(data, null, 2);
    }

    async function editArea(slug) {
      const res = await fetch(`${apiBase}/${slug}`);
      if (!res.ok) {
        setStatus("Nao foi possivel carregar area para edicao.", true);
        return;
      }
      const data = await res.json();
      editingSlug = slug;
      els.formTitle.textContent = `Editando: ${slug}`;
      els.name.value = data.name || "";
      els.slug.value = data.slug || "";
      els.agencia.value = data.agencia || "";
      els.relevancia.value = data.relevancia || 1;
      els.polygons.value = JSON.stringify(data.polygons || [], null, 2);
      els.areaJson.textContent = JSON.stringify(data, null, 2);
      setStatus("Modo edicao ativado.");
    }

    async function deleteArea(slug) {
      const ok = confirm(`Excluir a area '${slug}'?`);
      if (!ok) return;
      const res = await fetch(`${apiBase}/${slug}`, { method: "DELETE" });
      if (!res.ok) {
        const err = await res.json();
        setStatus(err.detail || "Erro ao excluir area.", true);
        return;
      }
      setStatus(`Area '${slug}' removida.`);
      if (editingSlug === slug) resetForm();
      await loadAreas();
    }

    async function saveArea(event) {
      event.preventDefault();

      let polygonsParsed;
      try {
        polygonsParsed = JSON.parse(els.polygons.value);
      } catch (error) {
        setStatus("JSON de polygons invalido.", true);
        return;
      }

      const payload = {
        name: els.name.value.trim(),
        slug: els.slug.value.trim(),
        agencia: els.agencia.value.trim(),
        relevancia: Number(els.relevancia.value),
        polygons: polygonsParsed,
      };

      const isEditingSameSlug = editingSlug && editingSlug === payload.slug;
      const method = isEditingSameSlug ? "PATCH" : "POST";
      const url = isEditingSameSlug ? `${apiBase}/${editingSlug}` : apiBase;
      const body = isEditingSameSlug
        ? JSON.stringify({
            name: payload.name,
            agencia: payload.agencia,
            relevancia: payload.relevancia,
            polygons: payload.polygons,
          })
        : JSON.stringify(payload);

      const res = await fetch(url, {
        method,
        headers: { "Content-Type": "application/json" },
        body,
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        setStatus(err.detail || "Falha ao salvar area.", true);
        return;
      }

      setStatus(isEditingSameSlug ? "Area atualizada com sucesso." : "Area salva com sucesso.");
      await loadAreas();
      if (!isEditingSameSlug) resetForm();
      await viewArea(payload.slug);
    }

    els.form.addEventListener("submit", saveArea);
    els.resetBtn.addEventListener("click", resetForm);

    resetForm();
    loadAreas().catch((err) => {
      els.listMeta.textContent = "Erro ao carregar.";
      setStatus(err.message || "Erro inesperado.", true);
    });

    window.viewArea = viewArea;
    window.editArea = editArea;
    window.deleteArea = deleteArea;
  </script>
</body>
</html>
"""


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def frontend():
    return FRONTEND_HTML


@app.post(
    "/api/v1/analyze",
    response_model=AnalysisResponse,
    summary="Analisa se um ponto esta dentro das areas solicitadas",
    tags=["Analise"],
)
def post_analyze(request: AnalysisRequest):
    return analyze(request)


@app.get(
    "/api/v1/areas",
    response_model=list[AreaSummary],
    summary="Lista todas as areas cadastradas",
    tags=["Areas"],
)
def list_areas():
    return repository.list_all()


@app.get(
    "/api/v1/areas/{slug}",
    summary="Retorna detalhes de uma area",
    tags=["Areas"],
)
def get_area(slug: str):
    data = repository.get_raw(slug)
    if data is None:
        raise HTTPException(404, f"Area '{slug}' nao encontrada.")
    return data


@app.post(
    "/api/v1/areas",
    status_code=201,
    summary="Cria ou atualiza uma area",
    tags=["Areas"],
)
def upsert_area(area: AreaInput):
    repository.upsert(area)
    return {"message": f"Area '{area.slug}' salva com sucesso."}


@app.patch(
    "/api/v1/areas/{slug}",
    summary="Atualiza parcialmente uma area existente",
    tags=["Areas"],
)
def patch_area(slug: str, patch: AreaPatchInput):
    if not repository.exists(slug):
        raise HTTPException(404, f"Area '{slug}' nao encontrada.")

    patch_dict = patch.model_dump(exclude_none=True)
    new_slug = patch_dict.get("slug")

    if new_slug and new_slug != slug and repository.exists(new_slug):
        raise HTTPException(409, f"Area '{new_slug}' ja existe.")

    updated = repository.patch(slug, patch_dict)
    if updated is None:
        raise HTTPException(404, f"Area '{slug}' nao encontrada.")

    return {
        "message": f"Area '{slug}' atualizada com sucesso.",
        "area": updated,
    }


@app.delete(
    "/api/v1/areas/{slug}",
    summary="Remove uma area",
    tags=["Areas"],
)
def delete_area(slug: str):
    if not repository.delete(slug):
        raise HTTPException(404, f"Area '{slug}' nao encontrada.")
    return {"message": f"Area '{slug}' removida."}
