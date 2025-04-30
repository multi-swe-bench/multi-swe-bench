#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout 03b616a1e015ff6ccfb665c5156e1b5359d2a6f1
bash /home/check_git_changes.sh

yarn install || true

