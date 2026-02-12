import json
import os
from pathlib import Path
from typing import Optional

from shapely.geometry import MultiPolygon, Polygon

from lib.models import AreaInput

AREAS_FILE = os.getenv("AREAS_FILE", "areas/areas.json")


class AreasRepository:
    """
    Armazena areas em JSON e mantem geometrias Shapely em memoria.

    Na Vercel (serverless), o filesystem e read-only em runtime.
    Escrita no JSON funciona em dev local. Em producao, o arquivo
    areas.json e lido do que esta commitado no repositorio.
    Para persistencia dinamica em producao, trocar por um banco
    (ex: Vercel KV, Supabase, Neon Postgres + PostGIS).
    """

    def __init__(self) -> None:
        self._areas_data: dict[str, dict] = {}
        self._geometries: dict[str, MultiPolygon] = {}
        self._load()

    def _load(self) -> None:
        path = Path(AREAS_FILE)
        if not path.exists():
            return
        # Accept files with or without UTF-8 BOM (common when edited on Windows)
        with open(path, "r", encoding="utf-8-sig") as f:
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
            # Vercel: filesystem read-only em producao; ignora silenciosamente
            pass

    @staticmethod
    def _ring_to_xy(ring: list[list[float]]) -> list[tuple[float, float]]:
        # GeoJSON position = [lng, lat, alt?]
        return [(position[0], position[1]) for position in ring]

    @staticmethod
    def _extract_coordinates(poly_data: dict) -> list[list[list[float]]]:
        if "coordinates" in poly_data:
            return poly_data["coordinates"]

        # Backward compatibility: old schema with points [lat, lng]
        if "points" in poly_data:
            return [[[point[1], point[0]] for point in poly_data["points"]]]

        raise ValueError("Polygon invalido: esperado 'coordinates' no padrao GeoJSON.")

    @classmethod
    def _build_geometry(cls, polygons_raw: list[dict]) -> MultiPolygon:
        polys: list[Polygon] = []
        for poly_data in polygons_raw:
            coordinates = cls._extract_coordinates(poly_data)
            shell = cls._ring_to_xy(coordinates[0])
            holes = [cls._ring_to_xy(ring) for ring in coordinates[1:]]
            polys.append(Polygon(shell=shell, holes=holes if holes else None))
        return MultiPolygon(polys)

    @staticmethod
    def _count_polygon_points(poly_data: dict) -> int:
        if "coordinates" in poly_data:
            return sum(len(ring) for ring in poly_data["coordinates"])
        if "points" in poly_data:
            return len(poly_data["points"])
        return 0

    def upsert(self, area: AreaInput) -> None:
        area_dict = area.model_dump()
        self._areas_data[area.slug] = area_dict
        self._geometries[area.slug] = self._build_geometry(area_dict["polygons"])
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
                "total_points": sum(
                    self._count_polygon_points(polygon) for polygon in data["polygons"]
                ),
            }
            for slug, data in self._areas_data.items()
        ]

    def exists(self, slug: str) -> bool:
        return slug in self._areas_data


repository = AreasRepository()
