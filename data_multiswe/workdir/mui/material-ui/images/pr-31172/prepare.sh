#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout ba0529496c52152b65b951a0ff09433260fea917
bash /home/check_git_changes.sh

yarn install || true

