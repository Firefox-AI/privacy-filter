"""Ray Serve app for openai/privacy-filter.

Token classifier that finds PII spans (names, emails, phones, addresses,
account numbers, URLs, dates, secrets) and optionally masks them. CPU-only.
The chart points at this module via serveConfig.import_path:
    privacy_filter.service:deployment
"""

import importlib.metadata
import logging
from typing import Annotated

from fastapi import FastAPI, HTTPException, Request, Security
from fastapi.exception_handlers import http_exception_handler
from ray import serve
from starlette.responses import JSONResponse

from privacy_filter.core.classes import (
    FilterRequest,
    FilterResponse,
    FilterResult,
    Span,
)
from privacy_filter.core.config import env
from privacy_filter.core.masking import MASK_TOKENS as MASK_TOKENS
from privacy_filter.core.masking import mask_text as _mask_text
from privacy_filter.core.utils import authorize_request


def _get_privacy_filter_version() -> str:
    try:
        return importlib.metadata.version("privacy-filter")
    except importlib.metadata.PackageNotFoundError:
        return "0.0.0"


privacy_filter_version = _get_privacy_filter_version()

app = FastAPI(title="privacy-filter", version="0.1.0")
_log = logging.getLogger(__name__)


@serve.deployment(ray_actor_options={"num_cpus": 2})
@serve.ingress(app)
class PrivacyFilterService:
    def __init__(self) -> None:
        from privacy_filter.core.logger import logger, setup_logger

        setup_logger()

        from transformers import pipeline

        _log.info("loading privacy-filter model_id=%s", env.MODEL_ID)
        self.classifier = pipeline(
            task="token-classification",
            model=env.MODEL_ID,
            aggregation_strategy="simple",
            device=-1,
        )
        self._ready = True
        _log.info("privacy-filter model loaded")

    def _classify_one(self, text: str, threshold: float) -> FilterResult:
        raw = self.classifier(text)
        spans = [
            Span(
                category=ent["entity_group"],
                text=ent["word"],
                start=int(ent["start"]),
                end=int(ent["end"]),
                score=float(ent["score"]),
            )
            for ent in raw
            if float(ent["score"]) >= threshold
        ]
        return FilterResult(spans=spans, masked_text=None)

    @app.exception_handler(HTTPException)
    async def log_and_handle_http_exception(request: Request, exc: HTTPException):
        """Logs HTTPExceptions"""
        _log.error(
            f"HTTPException for {request.method} {request.url.path} -> status={exc.status_code} detail={exc.detail}",
        )
        return await http_exception_handler(request, exc)

    @app.post("/privacy-filter", responses={401: {"description": "Invalid API key"}})
    async def privacy_filter(
        self, req: Annotated[FilterRequest, Security(authorize_request)]
    ) -> FilterResponse:
        """Filter text for PII spans.

        Requires the `x-pf-api-key` header to match `MASTER_KEY`.
        """
        results: list[FilterResult] = []
        for text in req.items:
            result = self._classify_one(text, req.threshold)
            if req.mask:
                result.masked_text = _mask_text(text, result.spans)
            results.append(result)
        return FilterResponse(
            results=results,
            model_id=env.MODEL_ID,
            num_items=len(req.items),
        )

    @app.get("/healthz")
    async def healthz(self) -> str:
        return "ok"

    @app.get("/readyz")
    async def readyz(self):
        if getattr(self, "_ready", False):
            return {
                "ready": True,
                "version": privacy_filter_version,
                "model_id": env.MODEL_ID,
            }
        return JSONResponse({"ready": False}, status_code=503)

    async def check_health(self) -> None:
        if not getattr(self, "_ready", False):
            raise RuntimeError("model not loaded")


deployment = PrivacyFilterService.bind()  # ty: ignore [unresolved-attribute]
