
ARG PY_VER=3.12.11-slim-trixie
ARG BUILDPLATFORM=${BUILDPLATFORM:-amd64}

FROM --platform=${BUILDPLATFORM} node:20-trixie-slim
COPY docker/ /app/docker/