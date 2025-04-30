#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout e6561e21bea65fb938470a9503971776a998196d
bash /home/check_git_changes.sh

yarn install || true

