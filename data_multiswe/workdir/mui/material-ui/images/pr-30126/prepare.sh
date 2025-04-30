#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout da1fdb481c234a53f6b1544d3c3f6d354a00330a
bash /home/check_git_changes.sh

yarn install || true

