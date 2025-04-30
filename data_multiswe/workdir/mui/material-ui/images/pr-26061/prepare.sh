#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout 5a983eadb806ba095de2a2754b208d470e3f55e7
bash /home/check_git_changes.sh

yarn install || true

