#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout a1e651f48deaabbe70ea1033e29e869906284b19
bash /home/check_git_changes.sh

yarn install || true

