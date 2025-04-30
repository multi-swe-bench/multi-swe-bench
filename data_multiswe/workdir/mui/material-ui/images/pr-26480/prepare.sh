#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout d81caa37668ad2d573c4c1ae518e306c5cebe2cf
bash /home/check_git_changes.sh

yarn install || true

