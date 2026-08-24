"""Local entrypoint for the privacy-filter Ray Serve application."""

import logging
import os

from ray import serve

from privacy_filter.core.config import env
from privacy_filter.core.service import deployment


def main() -> None:
    serve.start(http_options={"host": env.HOST, "port": env.PORT})
    serve.run(
        deployment,
        name="privacy-filter",
        route_prefix="/",
        blocking=True,
    )


if __name__ == "__main__":
    main()
