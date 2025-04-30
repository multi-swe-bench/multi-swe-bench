#!/bin/bash
set -e

cd /home/core
git reset --hard
bash /home/check_git_changes.sh
git checkout 4592b63c6a8a3d69bfe4ac1f9458b4a86a9676a4
bash /home/check_git_changes.sh

pnpm install || true

