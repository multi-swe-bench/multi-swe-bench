#!/bin/bash
set -e

cd /home/github-readme-stats
git reset --hard
bash /home/check_git_changes.sh
git checkout 60012707c7eaa51fd0377ce8ae46da6ebad24342
bash /home/check_git_changes.sh

npm install || true
npm ci || true

