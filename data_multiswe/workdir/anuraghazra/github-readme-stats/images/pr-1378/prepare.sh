#!/bin/bash
set -e

cd /home/github-readme-stats
git reset --hard
bash /home/check_git_changes.sh
git checkout 02ebd3243b4dc1aba224c7c75c23ebd3e4867ed2
bash /home/check_git_changes.sh

npm install || true
npm ci || true

