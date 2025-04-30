#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout c406cd6f89dcab6a223dbe77d833bc947ff64fdb
bash /home/check_git_changes.sh

yarn install || true

