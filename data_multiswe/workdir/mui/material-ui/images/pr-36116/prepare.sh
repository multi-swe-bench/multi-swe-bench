#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout f800c835562da9cc8fa3f7615b32a8e6cc8b31d8
bash /home/check_git_changes.sh

yarn install || true

