#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout 8d6bae2e39b9c6e28caf49e0fb930ccfba4b711f
bash /home/check_git_changes.sh

yarn install || true

