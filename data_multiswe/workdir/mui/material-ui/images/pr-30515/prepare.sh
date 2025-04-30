#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout 6b618938c28cc63728ae3d897d06c87a3c9736d3
bash /home/check_git_changes.sh

yarn install || true

