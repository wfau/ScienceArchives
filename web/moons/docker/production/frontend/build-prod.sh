#!/bin/bash

corepack enable

cp -r /mnt/web-ui /

cd /web-ui

pnpm install --frozen-lockfile
pnpm run build

cp -r /web-ui/dist /mnt/web-ui/