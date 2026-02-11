# Geo Analysis API

API REST para verificar se um ponto geográfico está dentro de áreas
poligonais e calcular a distância até a borda mais próxima.

## Deploy na Vercel

```bash
# 1. Instale a Vercel CLI
npm i -g vercel

# 2. Na raiz do projeto
vercel
```

Pronto. Sem configuração extra.

## Dev Local

```bash
pip install -r requirements.txt
pip install uvicorn

uvicorn api.index:app --reload
```

Docs: http://localhost:8000/docs

## Endpoints

### `POST /api/v1/analyze`

Verifica se o ponto está nas áreas solicitadas.

```json
{
  "target": { "lat": -23.555, "lng": -46.630 },
  "areas": ["area_principal", "area_completa"]
}
```

**Resposta:**

```json
{
  "results": {
    "area_principal": {
      "is_in": true,
      "nearest_border_distance_meters": 0
    },
    "area_completa": {
      "is_in": true,
      "nearest_border_distance_meters": 0
    }
  },
  "errors": null
}
```

### `GET /api/v1/areas` — Lista áreas
### `GET /api/v1/areas/{slug}` — Detalhes da área
### `POST /api/v1/areas` — Criar/atualizar área
### `DELETE /api/v1/areas/{slug}` — Remover área

## Persistência

As áreas são lidas de `areas/areas.json` (commitado no repo).
Na Vercel, o filesystem é read-only em runtime.

Para CRUD dinâmico em produção, substitua o repository por:
- Vercel KV / Vercel Postgres
- Supabase (Postgres + PostGIS)
- PlanetScale / Neon
