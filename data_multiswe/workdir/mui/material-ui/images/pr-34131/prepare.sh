#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout f2d6d61cc4d42b9b2ee9f5ea9ebf8aae192840d4
bash /home/check_git_changes.sh

yarn install || true

