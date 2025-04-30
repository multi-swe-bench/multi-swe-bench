#!/bin/bash
set -e

cd /home/github-readme-stats
git reset --hard
bash /home/check_git_changes.sh
git checkout 9fb28c91126d798b9f489dc25d0055b805cd40e6
bash /home/check_git_changes.sh

npm install || true
npm ci || true

