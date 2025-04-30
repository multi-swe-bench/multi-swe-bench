#!/bin/bash
set -e

cd /home/github-readme-stats
git reset --hard
bash /home/check_git_changes.sh
git checkout d57251cdf1cb5e7b6cea6081147eb9daf8257eef
bash /home/check_git_changes.sh

npm install || true
npm ci || true

