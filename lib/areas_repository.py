import json
import os
from copy import deepcopy
from threading import RLock
from typing import Optional

import boto3
from botocore.exceptions import ClientError
from shapely.geometry import MultiPolygon, Polygon

from lib.models import AreaInput
from lib.kml_service import maybe_refresh_automatic_area

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "https://minioconsole.shprimenegocios.com.br")
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "assets")
MINIO_OBJECT_KEY = os.getenv("MINIO_OBJECT_KEY", "areas/areas.json")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")
MINIO_REGION = os.getenv("MINIO_REGION", "us-east-1")


class AreasRepository:
    """
    Armazena areas no MinIO e mantem geometrias Shapely em memoria.

    Estrategia:
    - carrega do MinIO uma vez por instancia (cold start);
    - reaproveita cache em memoria entre requests;
    - se cache estiver vazio, tenta recarregar do MinIO.
    """

    def __init__(self) -> None:
        self._areas_data: dict[str, dict] = {}
        self._geometries: dict[str, MultiPolygon] = {}
        self._loaded = False
        self._lock = RLock()
        self._s3 = self._build_s3_client()

    @staticmethod
    def _build_s3_client():
        if not MINIO_ACCESS_KEY or not MINIO_SECRET_KEY:
            raise RuntimeError(
                "MINIO_ACCESS_KEY e MINIO_SECRET_KEY devem estar configuradas nas variaveis de ambiente."
            )

        return boto3.client(
            "s3",
            endpoint_url=MINIO_ENDPOINT,
            aws_access_key_id=MINIO_ACCESS_KEY,
            aws_secret_access_key=MINIO_SECRET_KEY,
            region_name=MINIO_REGION,
        )

    def _download_raw_areas(self) -> dict:
        try:
            response = self._s3.get_object(Bucket=MINIO_BUCKET, Key=MINIO_OBJECT_KEY)
        except ClientError as exc:
            code = exc.response.get("Error", {}).get("Code", "")
            if code in {"NoSuchKey", "404"}:
                return {}
            raise

        body = response["Body"].read()
        if not body or not body.strip():
            return {}

        data = json.loads(body.decode("utf-8-sig"))
        if not isinstance(data, dict):
            raise ValueError("Conteudo do arquivo de areas no MinIO deve ser um objeto JSON.")
        return data

    def _upload_raw_areas(self) -> None:
        payload = json.dumps(self._areas_data, ensure_ascii=False, indent=2).encode("utf-8")
        self._s3.put_object(
            Bucket=MINIO_BUCKET,
            Key=MINIO_OBJECT_KEY,
            Body=payload,
            ContentType="application/json; charset=utf-8",
        )

    @staticmethod
    def _normalize_area_record(area_dict: dict, slug_hint: Optional[str] = None) -> dict:
        normalized = deepcopy(area_dict)
        normalized["slug"] = str(normalized.get("slug") or slug_hint or "").strip()
        normalized["mode"] = str(normalized.get("mode") or "manual")
        if normalized["mode"] != "automatic":
            normalized["mode"] = "manual"
            normalized["automatic_source"] = None
            return normalized

        automatic_source = deepcopy(normalized.get("automatic_source") or {})
        automatic_source["type"] = str(automatic_source.get("type") or "kml_upload")
        if automatic_source["type"] not in {"kml_upload", "network_link"}:
            automatic_source["type"] = "kml_upload"
        if automatic_source["type"] != "network_link":
            automatic_source["refresh_interval_seconds"] = None
        normalized["automatic_source"] = automatic_source
        return normalized

    def _hydrate_from_raw(self, raw: dict) -> None:
        self._areas_data = {}
        self._geometries = {}
        for slug, area_dict in raw.items():
            normalized = self._normalize_area_record(area_dict, slug)
            self._areas_data[normalized["slug"]] = normalized
            self._geometries[normalized["slug"]] = self._build_geometry(normalized["polygons"])

    def _ensure_loaded(self) -> None:
        with self._lock:
            if self._loaded:
                return

            raw = self._download_raw_areas()
            self._hydrate_from_raw(raw)
            self._loaded = True

    @staticmethod
    def _ring_to_xy(ring: list[list[float]]) -> list[tuple[float, float]]:
        return [(position[0], position[1]) for position in ring]

    @staticmethod
    def _extract_coordinates(poly_data: dict) -> list[list[list[float]]]:
        if "coordinates" in poly_data:
            return poly_data["coordinates"]
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

    def _apply_area_record(self, area_dict: dict) -> None:
        normalized = self._normalize_area_record(area_dict, area_dict.get("slug"))
        slug = normalized["slug"]
        self._areas_data[slug] = normalized
        self._geometries[slug] = self._build_geometry(normalized["polygons"])

    def _refresh_area_locked(self, slug: str, force: bool = False) -> Optional[dict]:
        current = self._areas_data.get(slug)
        if current is None:
            return None

        refreshed = maybe_refresh_automatic_area(current, force=force)
        if refreshed != current:
            self._apply_area_record(refreshed)
            self._upload_raw_areas()

        return self._areas_data.get(slug)

    def refresh_area(self, slug: str, force: bool = False) -> Optional[dict]:
        with self._lock:
            self._ensure_loaded()
            return self._refresh_area_locked(slug, force=force)

    def refresh_all_automatic_areas(self) -> None:
        with self._lock:
            self._ensure_loaded()
            changed = False
            automatic_slugs = [
                slug for slug, data in self._areas_data.items() if data.get("mode") == "automatic"
            ]
            for slug in automatic_slugs:
                current = self._areas_data.get(slug)
                refreshed = maybe_refresh_automatic_area(current or {})
                if refreshed != current:
                    self._apply_area_record(refreshed)
                    changed = True
            if changed:
                self._upload_raw_areas()

    def upsert(self, area: AreaInput) -> None:
        with self._lock:
            self._ensure_loaded()
            area_dict = self._normalize_area_record(area.model_dump(), area.slug)
            self._apply_area_record(area_dict)
            self._upload_raw_areas()

    def patch(self, slug: str, changes: dict) -> Optional[dict]:
        with self._lock:
            self._ensure_loaded()
            current = self._areas_data.get(slug)
            if current is None:
                return None

            new_slug = changes.get("slug", slug)
            updated = {
                "name": changes.get("name", current["name"]),
                "slug": new_slug,
                "agencia": changes.get("agencia", current.get("agencia", "")),
                "relevancia": changes.get("relevancia", current.get("relevancia", 1)),
                "polygons": changes.get("polygons", current["polygons"]),
                "mode": changes.get("mode", current.get("mode", "manual")),
                "automatic_source": changes.get("automatic_source", current.get("automatic_source")),
            }

            self._apply_area_record(updated)

            if new_slug != slug:
                del self._areas_data[slug]
                del self._geometries[slug]

            self._upload_raw_areas()
            return self._areas_data.get(new_slug)

    def delete(self, slug: str) -> bool:
        with self._lock:
            self._ensure_loaded()
            if slug not in self._areas_data:
                return False
            del self._areas_data[slug]
            del self._geometries[slug]
            self._upload_raw_areas()
            return True

    def get_geometry(self, slug: str) -> Optional[MultiPolygon]:
        with self._lock:
            self._ensure_loaded()
            self._refresh_area_locked(slug)
            return self._geometries.get(slug)

    def get_raw(self, slug: str) -> Optional[dict]:
        with self._lock:
            self._ensure_loaded()
            return self._refresh_area_locked(slug)

    def find_slugs_by_agencias(self, agencias: list[str]) -> list[str]:
        with self._lock:
            self._ensure_loaded()
            normalized = {agencia.strip().casefold() for agencia in agencias}
            return [
                slug
                for slug, data in self._areas_data.items()
                if str(data.get("agencia", "")).strip().casefold() in normalized
            ]

    def list_all(self) -> list[dict]:
        with self._lock:
            self._ensure_loaded()
            automatic_slugs = [
                slug for slug, data in self._areas_data.items() if data.get("mode") == "automatic"
            ]
            changed = False
            for slug in automatic_slugs:
                current = self._areas_data.get(slug)
                refreshed = maybe_refresh_automatic_area(current or {})
                if refreshed != current:
                    self._apply_area_record(refreshed)
                    changed = True
            if changed:
                self._upload_raw_areas()

            return [
                {
                    "name": data["name"],
                    "slug": slug,
                    "polygon_count": len(data["polygons"]),
                    "total_points": sum(
                        self._count_polygon_points(polygon) for polygon in data["polygons"]
                    ),
                    "mode": data.get("mode", "manual"),
                    "automatic_source_type": (data.get("automatic_source") or {}).get("type"),
                    "last_refreshed_at": (data.get("automatic_source") or {}).get("last_refreshed_at"),
                    "last_refresh_attempt_at": (data.get("automatic_source") or {}).get("last_refresh_attempt_at"),
                    "last_refresh_error": (data.get("automatic_source") or {}).get("last_refresh_error"),
                }
                for slug, data in self._areas_data.items()
            ]

    def exists(self, slug: str) -> bool:
        with self._lock:
            self._ensure_loaded()
            return slug in self._areas_data


repository = AreasRepository()
