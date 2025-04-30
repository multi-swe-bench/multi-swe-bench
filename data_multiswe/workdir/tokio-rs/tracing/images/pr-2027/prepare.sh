#!/bin/bash
set -e

cd /home/tracing
git reset --hard
bash /home/check_git_changes.sh
git checkout f58019e1a67cc98e87ad15bf42269fddbc271e36
bash /home/check_git_changes.sh

cargo test || true

