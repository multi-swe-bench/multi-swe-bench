#!/bin/bash
set -e

cd /home/core
git reset --hard
bash /home/check_git_changes.sh
git checkout fc772dbf7398e8ce961025556594b4a7d3f64871
bash /home/check_git_changes.sh

pnpm install || true

