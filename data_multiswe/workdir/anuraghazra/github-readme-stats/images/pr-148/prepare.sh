#!/bin/bash
set -e

cd /home/github-readme-stats
git reset --hard
bash /home/check_git_changes.sh
git checkout aa44bd7615442cc927ac070c5aedf35cb865c3a2
bash /home/check_git_changes.sh

npm install || true
npm ci || true

