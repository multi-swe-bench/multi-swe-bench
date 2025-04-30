#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout 4f6c184c749b9ef1819b52a54e6db76c26f14482
bash /home/check_git_changes.sh

yarn install || true

