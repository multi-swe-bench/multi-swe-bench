#!/bin/bash
set -e

cd /home/github-readme-stats
git reset --hard
bash /home/check_git_changes.sh
git checkout 96f89ad2b7ef282b3dc15642e3c658af86972b19
bash /home/check_git_changes.sh

npm install || true
npm ci || true

