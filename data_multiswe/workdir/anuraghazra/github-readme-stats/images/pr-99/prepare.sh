#!/bin/bash
set -e

cd /home/github-readme-stats
git reset --hard
bash /home/check_git_changes.sh
git checkout b039fa16afedf91cc9044f790ec63f23dbfa0299
bash /home/check_git_changes.sh

npm install || true
npm ci || true

