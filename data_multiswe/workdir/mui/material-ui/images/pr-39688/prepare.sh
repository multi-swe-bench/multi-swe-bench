#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout f69997e32614d07f26782dddd0fb6f96c67c3c4d
bash /home/check_git_changes.sh

yarn install || true

