# Omnipy runner image: Python and Omnipy, for running jobs on other machines, such as TES nodes,
# with `python -m omnipy run`. Users' own code and dependencies are installed per job.
#
# Release build:     --build-arg OMNIPY_VERSION=0.24.0 --build-arg PYTHON_VERSION=3.12
# Development build: uv build && docker build --build-context wheels=dist ... (see README.md)

ARG PYTHON_VERSION=3.12

# Empty by default. A development build replaces this stage with a directory of wheels through
# `--build-context wheels=<dir>`, and the image then installs Omnipy from those wheels.
FROM scratch AS wheels

FROM python:${PYTHON_VERSION}-slim

ARG OMNIPY_VERSION

LABEL org.opencontainers.image.source=https://github.com/fairtracks/omnipy
LABEL org.opencontainers.image.description="Omnipy runner for remote job execution"

COPY --from=wheels / /tmp/wheels/

RUN set -eu; \
    if ls /tmp/wheels/*.whl >/dev/null 2>&1; then \
        pip install --no-cache-dir /tmp/wheels/*.whl; \
    else \
        test -n "${OMNIPY_VERSION:-}" \
            || { echo 'Build with --build-arg OMNIPY_VERSION=<version>' >&2; exit 1; }; \
        pip install --no-cache-dir "omnipy==${OMNIPY_VERSION}"; \
    fi; \
    rm -rf /tmp/wheels; \
    pip check; \
    python -c 'import omnipy; print("omnipy", omnipy.__version__)'

RUN useradd --create-home omnipy
USER omnipy
WORKDIR /home/omnipy

ENV PYTHONUNBUFFERED=1

CMD ["python", "-m", "omnipy", "--help"]
