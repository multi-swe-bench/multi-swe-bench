#!/bin/bash
set -e

cd /home/github-readme-stats
git reset --hard
bash /home/check_git_changes.sh
git checkout 99591915eceb5136c0882037aa893cda5b5dbb34
bash /home/check_git_changes.sh

npm install || true
npm ci || true

