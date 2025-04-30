#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout 1e09429e1804ddd7505fe78f3d606e24e98aa16f
bash /home/check_git_changes.sh

yarn install || true

