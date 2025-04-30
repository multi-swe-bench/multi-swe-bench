#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout d88ab9ebdc63157a7efcf582e65d4f6c58e5f576
bash /home/check_git_changes.sh

yarn install || true

