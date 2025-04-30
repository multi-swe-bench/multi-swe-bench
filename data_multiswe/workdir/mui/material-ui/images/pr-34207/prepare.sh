#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout 1a4263a50af00eaffdca2e58b8ff16d62c4408a7
bash /home/check_git_changes.sh

yarn install || true

