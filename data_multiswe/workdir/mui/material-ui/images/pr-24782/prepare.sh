#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout 058e409679188b9b5d68baeabea9f46b21f7fe1f
bash /home/check_git_changes.sh

yarn install || true

