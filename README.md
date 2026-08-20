# privacy-filter

FastAPI and Ray Serve app for `openai/privacy-filter`.

The service loads the Hugging Face token-classification model in a Ray Serve actor, finds PII spans, and can return either spans only or masked text.

## Setup

```bash
make setup
```

This creates `.venv/`, installs dependencies with uv, and installs the local pre-commit hooks.

## Run Locally

```bash
make serve
```

The service listens on `0.0.0.0:8080` by default. Override with `HOST` or `PORT`:

```bash
PORT=8000 make serve
```

Ray Serve import path for charts or `serveConfig`:

```text
privacy_filter.service:deployment
```

## Docker

```bash
make docker-build
make docker-run
```

Equivalent commands:

```bash
docker build -t privacy-filter:local .
docker run --rm -p 8080:8080 privacy-filter:local
```

## Configuration

`MODEL_ID` changes the model loaded by the Serve actor. It defaults to `openai/privacy-filter`.
`MASTER_KEY` sets the API key required by `POST /filter`.

```bash
MASTER_KEY=sk-default MODEL_ID=openai/privacy-filter make serve
```

## API

Health checks:

```bash
curl http://localhost:8080/healthz
curl http://localhost:8080/readyz
```

Filter text:

```bash
curl -X POST http://localhost:8080/filter \
  -H "content-type: application/json" \
  -H "x-pf-api-key: $MASTER_KEY" \
  -d '{
    "items": ["Email jane@example.com or call 555-0100."],
    "mask": true,
    "threshold": 0.5
  }'
```

`POST /filter` requires the `x-pf-api-key` header. Its value must match the
service `MASTER_KEY` environment variable. Health check endpoints do not require
an API key.

Response shape:

```json
{
  "results": [
    {
      "masked_text": "Email [EMAIL] or call [PHONE].",
      "spans": [
        {
          "category": "email",
          "text": "jane@example.com",
          "start": 6,
          "end": 22,
          "score": 0.99
        }
      ]
    }
  ],
  "model_id": "openai/privacy-filter",
  "num_items": 1
}
```

Swagger UI is available at `http://localhost:8080/docs` when the service is running.

## Development

```bash
make test
make lint
```
