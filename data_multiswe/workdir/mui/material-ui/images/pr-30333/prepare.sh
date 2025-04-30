#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout e47f22b9ea22bb61b10b6bbd0789781a779eb529
bash /home/check_git_changes.sh

yarn install || true

