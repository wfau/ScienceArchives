FROM node:22-slim AS build
ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"
RUN corepack enable
WORKDIR /app

COPY query-ui/web-ui/package.json query-ui/web-ui/pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

COPY query-ui/web-ui/ ./
RUN pnpm approve-builds esbuild
RUN pnpm run build

FROM caddy:2
COPY --from=build /app/dist /frontend/frontend