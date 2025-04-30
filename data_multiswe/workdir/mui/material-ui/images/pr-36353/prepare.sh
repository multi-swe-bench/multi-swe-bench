#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout d57bd96cfcec023238c85488a3d399534518fd37
bash /home/check_git_changes.sh

yarn install || true

