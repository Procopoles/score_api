from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator, model_validator


class PointInput(BaseModel):
    lat: float = Field(..., description="Latitude do ponto alvo", ge=-90, le=90)
    lng: float = Field(..., description="Longitude do ponto alvo", ge=-180, le=180)


class AnalysisRequest(BaseModel):
    target: PointInput
    areas: list[str] = Field(
        ...,
        description="Slugs das areas a analisar",
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


class AreaResult(BaseModel):
    is_in: bool = Field(..., description="Ponto esta dentro da area?")
    nearest_border_distance_meters: float = Field(
        ...,
        description="Distancia em metros ate a borda mais proxima (0 se dentro)",
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


class PolygonInput(BaseModel):
    """
    GeoJSON Polygon:
    - type = "Polygon"
    - coordinates = [ [ [lng, lat, alt?], ... ] , ... ]
    """

    type: Literal["Polygon"] = "Polygon"
    coordinates: list[list[list[float]]] = Field(
        ...,
        min_length=1,
        description="Aneis GeoJSON no formato [lng, lat, alt?]. O primeiro anel e o externo.",
    )

    @field_validator("coordinates")
    @classmethod
    def validate_coordinates(
        cls,
        coordinates: list[list[list[float]]],
    ) -> list[list[list[float]]]:
        for ring in coordinates:
            if len(ring) < 4:
                raise ValueError("Cada anel do Polygon deve ter ao menos 4 posicoes.")

            for position in ring:
                if len(position) < 2:
                    raise ValueError("Cada posicao deve conter ao menos [lng, lat].")

                lng = position[0]
                lat = position[1]
                if not (-180 <= lng <= 180):
                    raise ValueError("Longitude fora do intervalo valido (-180 a 180).")
                if not (-90 <= lat <= 90):
                    raise ValueError("Latitude fora do intervalo valido (-90 a 90).")

        return coordinates


class AreaInput(BaseModel):
    """
    Area geografica. Aceita multiplos polygons (ilhas separadas).
    """

    name: str = Field(..., description="Nome legivel (ex: 'Area Principal')")
    slug: str = Field(
        ...,
        description="Identificador unico (ex: 'area_principal')",
        pattern=r"^[a-z0-9_]+$",
    )
    agencia: str = Field(..., description="Nome da agencia/unidade da imobiliaria (ex: SH Perdizes)")
    relevancia: int = Field(..., description="Nivel de relevancia da area (1 a 10)", ge=1, le=10)
    polygons: list[PolygonInput] = Field(..., min_length=1)

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Area Principal",
                    "slug": "area_principal",
                    "agencia": "SH Perdizes",
                    "relevancia": 8,
                    "polygons": [
                        {
                            "type": "Polygon",
                            "coordinates": [
                                [
                                    [-46.640, -23.550, 0],
                                    [-46.620, -23.550, 0],
                                    [-46.620, -23.560, 0],
                                    [-46.640, -23.560, 0],
                                    [-46.640, -23.550, 0]
                                ]
                            ]
                        }
                    ],
                }
            ]
        }
    }


class AreaPatchInput(BaseModel):
    name: Optional[str] = Field(default=None, description="Novo nome da area")
    slug: Optional[str] = Field(
        default=None,
        description="Novo identificador unico",
        pattern=r"^[a-z0-9_]+$",
    )
    agencia: Optional[str] = Field(
        default=None,
        description="Novo nome da agencia/unidade da imobiliaria",
    )
    relevancia: Optional[int] = Field(
        default=None,
        description="Novo nivel de relevancia da area (1 a 10)",
        ge=1,
        le=10,
    )
    polygons: Optional[list[PolygonInput]] = Field(
        default=None,
        min_length=1,
        description="Novo conjunto de polygons GeoJSON",
    )

    @model_validator(mode="after")
    def validate_at_least_one_field(self):
        if (
            self.name is None
            and self.slug is None
            and self.agencia is None
            and self.relevancia is None
            and self.polygons is None
        ):
            raise ValueError(
                "Informe ao menos um campo para atualizar: name, slug, agencia, relevancia ou polygons."
            )
        return self


class AreaSummary(BaseModel):
    name: str
    slug: str
    polygon_count: int
    total_points: int
