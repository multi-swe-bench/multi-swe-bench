#!/bin/bash
set -e

cd /home/github-readme-stats
git reset --hard
bash /home/check_git_changes.sh
git checkout 2efb399f33d8f3dca7eb156404598384f419cb8b
bash /home/check_git_changes.sh

npm install || true
npm ci || true

