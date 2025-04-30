#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout 0500cab4f0491a5e89648ce03e9dc5a769b76e21
bash /home/check_git_changes.sh

yarn install || true

