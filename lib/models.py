from pydantic import BaseModel, Field
from typing import Optional


# ──────────────────────────────────────────────
# REQUEST
# ──────────────────────────────────────────────

class PointInput(BaseModel):
    lat: float = Field(..., description="Latitude do ponto alvo", ge=-90, le=90)
    lng: float = Field(..., description="Longitude do ponto alvo", ge=-180, le=180)


class AnalysisRequest(BaseModel):
    target: PointInput
    areas: list[str] = Field(
        ...,
        description="Slugs das áreas a analisar",
        min_length=1,
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "target": {"lat": -23.555, "lng": -46.630},
                    "areas": ["area_principal", "area_completa"],
                }
            ]
        }
    }


# ──────────────────────────────────────────────
# RESPONSE
# ──────────────────────────────────────────────

class AreaResult(BaseModel):
    is_in: bool = Field(..., description="Ponto está dentro da área?")
    nearest_border_distance_meters: float = Field(
        ...,
        description="Distância em metros até a borda mais próxima (0 se dentro)",
    )


class AnalysisResponse(BaseModel):
    results: dict[str, AreaResult]
    errors: Optional[list[str]] = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "results": {
                        "area_principal": {
                            "is_in": False,
                            "nearest_border_distance_meters": 1028.43,
                        },
                        "area_completa": {
                            "is_in": True,
                            "nearest_border_distance_meters": 0,
                        },
                    },
                    "errors": None,
                }
            ]
        }
    }


# ──────────────────────────────────────────────
# CRUD DE ÁREAS
# ──────────────────────────────────────────────

class PolygonInput(BaseModel):
    """
    Lista de pontos [lat, lng] formando um polígono.
    Não precisa repetir o primeiro ponto no final.
    """
    points: list[list[float]] = Field(..., min_length=3)


class AreaInput(BaseModel):
    """
    Área geográfica. Aceita múltiplos polígonos (ilhas separadas).
    """
    name: str = Field(..., description="Nome legível (ex: 'Área Principal')")
    slug: str = Field(
        ...,
        description="Identificador único (ex: 'area_principal')",
        pattern=r"^[a-z0-9_]+$",
    )
    polygons: list[PolygonInput] = Field(..., min_length=1)

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Área Principal",
                    "slug": "area_principal",
                    "polygons": [
                        {
                            "points": [
                                [-23.550, -46.640],
                                [-23.550, -46.620],
                                [-23.560, -46.620],
                                [-23.560, -46.640],
                            ]
                        }
                    ],
                }
            ]
        }
    }


class AreaSummary(BaseModel):
    name: str
    slug: str
    polygon_count: int
    total_points: int
