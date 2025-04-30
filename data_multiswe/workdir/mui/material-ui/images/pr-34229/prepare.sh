#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout fa62bf35e109ede215cb8cbae66ba4d6a30fef60
bash /home/check_git_changes.sh

yarn install || true

