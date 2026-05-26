#!/bin/bash

corepack enable

cp -r /mnt/web-ui /

cd /web-ui
rm -r node_modules
rm -r dist

pnpm install --frozen-lockfile
pnpm approve-builds esbuild
pnpm run build

cp -r /web-ui/dist /mnt/web-ui/