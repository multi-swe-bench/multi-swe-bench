#!/bin/bash
set -e

cd /home/github-readme-stats
git reset --hard
bash /home/check_git_changes.sh
git checkout 112000667c01f18fd161f204ae3ee796ec2e3011
bash /home/check_git_changes.sh

npm install || true
npm ci || true

