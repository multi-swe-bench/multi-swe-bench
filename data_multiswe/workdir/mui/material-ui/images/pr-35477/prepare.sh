#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout e195455738a9de164d1f9766de96213b83dd6623
bash /home/check_git_changes.sh

yarn install || true

