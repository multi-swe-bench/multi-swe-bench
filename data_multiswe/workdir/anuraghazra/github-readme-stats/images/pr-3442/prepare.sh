#!/bin/bash
set -e

cd /home/github-readme-stats
git reset --hard
bash /home/check_git_changes.sh
git checkout 9c6eb2286284a44ea3ba983ab4d2d2f8a8c2203e
bash /home/check_git_changes.sh

npm install || true
npm ci || true

