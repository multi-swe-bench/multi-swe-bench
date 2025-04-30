#!/bin/bash
set -e

cd /home/github-readme-stats
git reset --hard
bash /home/check_git_changes.sh
git checkout 8e3147014ca6ef63033574f12c70c1372ec26db8
bash /home/check_git_changes.sh

npm install || true
npm ci || true

