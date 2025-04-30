#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout 8f246c16a78968aec03a13835bc5c7c74ea3d945
bash /home/check_git_changes.sh

yarn install || true

