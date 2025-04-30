#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout 984645eb1a765abbf39a4f61dad0d21a6e518ee3
bash /home/check_git_changes.sh

yarn install || true

