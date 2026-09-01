FROM rayproject/ray:2.50.1-py311

USER root

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

ENV HOST=0.0.0.0 \
    PORT=8080 \
    PYTHONPATH=/app \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    RAY_START_ARGS="--head --dashboard-host=0.0.0.0"

# CPU torch from the dedicated index so we don't pull CUDA wheels.
# Pin Ray to the chart's rayVersion (values.yaml).
RUN uv pip install --system \
      --index-url https://download.pytorch.org/whl/cpu \
      --extra-index-url https://pypi.org/simple \
      "ray[serve]==2.50.1" \
      fastapi \
      loguru \
      pydantic \
      pydantic-settings \
      starlette \
      uvicorn \
      "transformers>=4.44" \
      "torch>=2.2"

# Bake weights into the image for deterministic, network-free cold starts
# (~2-4GB). Drop this to download at runtime instead (needs an HF cache + egress).
ENV HF_HOME=/opt/hf-cache
RUN mkdir -p "${HF_HOME}" \
    && chown -R 1000:1000 "${HF_HOME}" /app \
    && chmod -R a+rwX "${HF_HOME}" \
    && chmod -R a+rX /app

USER ray

RUN python -c "from transformers import pipeline; \
    pipeline(task='token-classification', model='openai/privacy-filter')"

# Runtime should use the baked model cache instead of checking Hugging Face.
ENV HF_HUB_OFFLINE=1 \
    TRANSFORMERS_OFFLINE=1

COPY --chown=1000:1000 src/privacy_filter ./privacy_filter

EXPOSE 8000 8080 8265

CMD ["bash", "-lc", "ray start ${RAY_START_ARGS} --block"]
