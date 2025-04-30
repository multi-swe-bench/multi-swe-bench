#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout d687a88c1f4377b848730782890823c59de996e5
bash /home/check_git_changes.sh

yarn install || true

