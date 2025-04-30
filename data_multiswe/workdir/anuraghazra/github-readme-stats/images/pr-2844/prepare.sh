#!/bin/bash
set -e

cd /home/github-readme-stats
git reset --hard
bash /home/check_git_changes.sh
git checkout c5d4bcbc1ac5e1811681e4acd825cd39145fb2d9
bash /home/check_git_changes.sh

npm install || true
npm ci || true

