#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout d35d22994887bd83517a99cc8125ad97c402223a
bash /home/check_git_changes.sh

yarn install || true

