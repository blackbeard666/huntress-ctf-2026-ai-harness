#!/usr/bin/env bash
# @electron/asar: list/extract Electron app.asar archives.
source "$(dirname "$0")/_lib.sh"
npm install -s --prefix tools/npm-asar @electron/asar >/dev/null
link "$ROOT/tools/npm-asar/node_modules/.bin/asar" asar
