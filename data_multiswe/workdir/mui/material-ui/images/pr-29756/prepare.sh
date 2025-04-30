#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout 259952855e31dfde8c9daa3d7d00f6d88e35f27b
bash /home/check_git_changes.sh

yarn install || true

