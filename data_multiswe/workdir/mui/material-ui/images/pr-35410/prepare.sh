#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout 1e4dd5f0837c84a4f1a55590857f989d6c3198fc
bash /home/check_git_changes.sh

yarn install || true

