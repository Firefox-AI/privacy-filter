FROM python:3.12-slim

ENV HOST=0.0.0.0 \
    PORT=8080 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir uv==0.10.8
RUN uv pip install --system --editable .

EXPOSE 8080

CMD ["/usr/local/bin/privacy-filter"]
