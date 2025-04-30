#!/bin/bash
set -e

cd /home/github-readme-stats
git reset --hard
bash /home/check_git_changes.sh
git checkout d0ab2ff030edfecf74373de8ca16e9d09a273afa
bash /home/check_git_changes.sh

npm install || true
npm ci || true

