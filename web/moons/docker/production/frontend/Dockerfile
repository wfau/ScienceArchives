FROM node:20-slim AS base
ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"
COPY ./docker/production/frontend/build-prod.sh /app/build-prod.sh
WORKDIR /app

CMD ["/app/build-prod.sh"]
