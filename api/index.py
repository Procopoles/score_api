"""
Entrypoint Vercel - expoe a variavel `app` (FastAPI/ASGI).
"""

from fastapi import FastAPI, HTTPException
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


@app.get("/health")
def health():
    return {"status": "ok"}


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
