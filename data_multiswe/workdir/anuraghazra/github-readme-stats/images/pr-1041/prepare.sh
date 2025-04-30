#!/bin/bash
set -e

cd /home/github-readme-stats
git reset --hard
bash /home/check_git_changes.sh
git checkout fef8bc3a4a4ddb12a5c779e7cae18438231845a7
bash /home/check_git_changes.sh

npm install || true
npm ci || true

