#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout bb0bbe22d77dabe69cd6cd64971158aaa70068c4
bash /home/check_git_changes.sh

yarn install || true

