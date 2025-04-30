#!/bin/bash
set -e

cd /home/svelte
git reset --hard
bash /home/check_git_changes.sh
git checkout 86ef18165f35d132f77b711263f00899f8134554
bash /home/check_git_changes.sh

pnpm install --frozen-lockfile || true

