#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout ed32fe693fb46196d9faa8073387f16e2350fbdf
bash /home/check_git_changes.sh

yarn install || true

