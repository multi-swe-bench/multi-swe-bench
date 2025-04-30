#!/bin/bash
set -e

cd /home/github-readme-stats
git reset --hard
bash /home/check_git_changes.sh
git checkout e1932fdf7479fd48051de5ec788fcb76d4e783f0
bash /home/check_git_changes.sh

npm install || true
npm ci || true

