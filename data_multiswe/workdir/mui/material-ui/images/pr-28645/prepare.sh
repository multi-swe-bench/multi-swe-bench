#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout 26a6e51de4993f1bc26304f4af8b02d7fbb367ad
bash /home/check_git_changes.sh

yarn install || true

