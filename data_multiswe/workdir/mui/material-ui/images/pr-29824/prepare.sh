#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout b714f102d190358ab543e425de84325f81b6083a
bash /home/check_git_changes.sh

yarn install || true

