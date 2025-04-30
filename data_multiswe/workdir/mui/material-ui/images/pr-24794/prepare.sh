#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout f0e657bcd52071fb11b27437053ee6110a69b285
bash /home/check_git_changes.sh

yarn install || true

