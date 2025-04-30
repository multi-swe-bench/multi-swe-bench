#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout e6666a5b3887d6c7d4d6ee171a440f032d89462b
bash /home/check_git_changes.sh

yarn install || true

