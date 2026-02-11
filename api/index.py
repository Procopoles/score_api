"""
Entrypoint Vercel — expõe a variável `app` (FastAPI/ASGI).
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from lib.models import (
    AnalysisRequest,
    AnalysisResponse,
    AreaInput,
    AreaSummary,
)
from lib.geo_service import analyze
from lib.areas_repository import repository

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# APP
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

app = FastAPI(
    title="Geo Analysis API",
    description=(
        "Verifica se um ponto está dentro de áreas geográficas "
        "e calcula a distância até a borda mais próxima."
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


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# HEALTH
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.get("/health")
def health():
    return {"status": "ok"}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ANÁLISE GEOESPACIAL
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.post(
    "/api/v1/analyze",
    response_model=AnalysisResponse,
    summary="Analisa se um ponto está dentro das áreas solicitadas",
    tags=["Análise"],
)
def post_analyze(request: AnalysisRequest):
    return analyze(request)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CRUD DE ÁREAS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.get(
    "/api/v1/areas",
    response_model=list[AreaSummary],
    summary="Lista todas as áreas cadastradas",
    tags=["Áreas"],
)
def list_areas():
    return repository.list_all()


@app.get(
    "/api/v1/areas/{slug}",
    summary="Retorna detalhes de uma área",
    tags=["Áreas"],
)
def get_area(slug: str):
    data = repository.get_raw(slug)
    if data is None:
        raise HTTPException(404, f"Área '{slug}' não encontrada.")
    return data


@app.post(
    "/api/v1/areas",
    status_code=201,
    summary="Cria ou atualiza uma área",
    tags=["Áreas"],
)
def upsert_area(area: AreaInput):
    repository.upsert(area)
    return {"message": f"Área '{area.slug}' salva com sucesso."}


@app.delete(
    "/api/v1/areas/{slug}",
    summary="Remove uma área",
    tags=["Áreas"],
)
def delete_area(slug: str):
    if not repository.delete(slug):
        raise HTTPException(404, f"Área '{slug}' não encontrada.")
    return {"message": f"Área '{slug}' removida."}
