#!/bin/bash
set -e

cd /home/github-readme-stats
git reset --hard
bash /home/check_git_changes.sh
git checkout b4a9bd4468cfddfac0b556c16ead03f0683a2656
bash /home/check_git_changes.sh

npm install || true
npm ci || true

