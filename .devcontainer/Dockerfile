FROM ghcr.io/astral-sh/uv:latest AS uv

FROM mcr.microsoft.com/devcontainers/python:3.12-bullseye
COPY --from=uv --chown=vscode: /uv /uvx /bin/