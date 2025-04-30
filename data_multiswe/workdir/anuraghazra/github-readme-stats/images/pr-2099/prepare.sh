#!/bin/bash
set -e

cd /home/github-readme-stats
git reset --hard
bash /home/check_git_changes.sh
git checkout daa1977ba310f5dcb44f7945e7ecb5537e708c05
bash /home/check_git_changes.sh

npm install || true
npm ci || true

