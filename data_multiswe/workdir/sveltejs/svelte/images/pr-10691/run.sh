#!/bin/bash
set -e

cd /home/svelte
pnpm test -- --reporter verbose

