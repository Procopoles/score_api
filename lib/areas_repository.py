import json
import os
from pathlib import Path
from typing import Optional

from shapely.geometry import Polygon, MultiPolygon

from lib.models import AreaInput

AREAS_FILE = os.getenv("AREAS_FILE", "areas/areas.json")


class AreasRepository:
    """
    Armazena áreas em JSON e mantém geometrias Shapely em memória.

    Na Vercel (serverless), o filesystem é read-only em runtime.
    Escrita no JSON funciona em dev local. Em produção, o arquivo
    areas.json é lido do que está commitado no repositório.
    Para persistência dinâmica em produção, trocar por um banco
    (ex: Vercel KV, Supabase, Neon Postgres + PostGIS).
    """

    def __init__(self) -> None:
        self._areas_data: dict[str, dict] = {}
        self._geometries: dict[str, MultiPolygon] = {}
        self._load()

    # ── Persistência ─────────────────────────────

    def _load(self) -> None:
        path = Path(AREAS_FILE)
        if not path.exists():
            return
        with open(path, "r", encoding="utf-8") as f:
            raw: dict = json.load(f)
        for slug, area_dict in raw.items():
            self._areas_data[slug] = area_dict
            self._geometries[slug] = self._build_geometry(area_dict["polygons"])

    def _save(self) -> None:
        path = Path(AREAS_FILE)
        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self._areas_data, f, ensure_ascii=False, indent=2)
        except OSError:
            # Vercel: filesystem read-only em produção — ignora silenciosamente
            pass

    # ── Conversão para Shapely ───────────────────

    @staticmethod
    def _build_geometry(polygons_raw: list[dict]) -> MultiPolygon:
        polys: list[Polygon] = []
        for poly_data in polygons_raw:
            # Entrada: [lat, lng] → Shapely: (lng, lat) = (x, y)
            coords = [(p[1], p[0]) for p in poly_data["points"]]
            polys.append(Polygon(coords))
        return MultiPolygon(polys)

    # ── CRUD ─────────────────────────────────────

    def upsert(self, area: AreaInput) -> None:
        area_dict = area.model_dump()
        self._areas_data[area.slug] = area_dict
        self._geometries[area.slug] = self._build_geometry(
            [p.model_dump() for p in area.polygons]
        )
        self._save()

    def delete(self, slug: str) -> bool:
        if slug not in self._areas_data:
            return False
        del self._areas_data[slug]
        del self._geometries[slug]
        self._save()
        return True

    def get_geometry(self, slug: str) -> Optional[MultiPolygon]:
        return self._geometries.get(slug)

    def get_raw(self, slug: str) -> Optional[dict]:
        return self._areas_data.get(slug)

    def list_all(self) -> list[dict]:
        return [
            {
                "name": data["name"],
                "slug": slug,
                "polygon_count": len(data["polygons"]),
                "total_points": sum(len(p["points"]) for p in data["polygons"]),
            }
            for slug, data in self._areas_data.items()
        ]

    def exists(self, slug: str) -> bool:
        return slug in self._areas_data


# Singleton — carregado uma vez por cold start
repository = AreasRepository()
