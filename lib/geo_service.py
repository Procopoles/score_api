import math

from shapely.geometry import Point

from lib.areas_repository import repository
from lib.models import AnalysisRequest, AnalysisResponse, AreaResult

EARTH_RADIUS_M = 6_371_000


def _haversine(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Distância Haversine entre dois pontos em metros."""
    lat1, lng1, lat2, lng2 = map(math.radians, [lat1, lng1, lat2, lng2])
    dlat = lat2 - lat1
    dlng = lng2 - lng1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng / 2) ** 2
    return 2 * EARTH_RADIUS_M * math.asin(math.sqrt(a))


def _nearest_border_distance_meters(
    target_lat: float,
    target_lng: float,
    geometry,
) -> float:
    """
    Encontra o ponto mais próximo na borda do polígono (via Shapely)
    e calcula a distância real com Haversine.
    """
    target_point = Point(target_lng, target_lat)
    # nearest_points retorna o ponto na borda mais próximo
    nearest_on_border = geometry.boundary.interpolate(
        geometry.boundary.project(target_point)
    )
    return _haversine(
        target_lat, target_lng,
        nearest_on_border.y, nearest_on_border.x,  # y=lat, x=lng
    )


def analyze(request: AnalysisRequest) -> AnalysisResponse:
    target = Point(request.target.lng, request.target.lat)
    results: dict[str, AreaResult] = {}
    errors: list[str] = []

    for slug in request.areas:
        geometry = repository.get_geometry(slug)

        if geometry is None:
            errors.append(f"Área '{slug}' não encontrada.")
            continue

        is_inside = geometry.contains(target) or geometry.touches(target)

        if is_inside:
            distance_m = 0.0
        else:
            distance_m = round(
                _nearest_border_distance_meters(
                    request.target.lat,
                    request.target.lng,
                    geometry,
                ),
                2,
            )

        results[slug] = AreaResult(
            is_in=is_inside,
            nearest_border_distance_meters=distance_m,
        )

    return AnalysisResponse(
        results=results,
        errors=errors if errors else None,
    )
