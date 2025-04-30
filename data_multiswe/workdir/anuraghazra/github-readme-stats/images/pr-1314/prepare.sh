#!/bin/bash
set -e

cd /home/github-readme-stats
git reset --hard
bash /home/check_git_changes.sh
git checkout 4dbb9e93b9be070169228d89bff9a82342587a81
bash /home/check_git_changes.sh

npm install || true
npm ci || true

