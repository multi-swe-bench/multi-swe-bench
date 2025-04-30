#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout d428acb95ca37028d9e5be4f87c13e0d1088fa42
bash /home/check_git_changes.sh

yarn install || true

