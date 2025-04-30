#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout 5b53f5efe691a76630e479245e5be0f91371f691
bash /home/check_git_changes.sh

yarn install || true

