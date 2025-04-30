#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout a0c6c43187da86b1538685afdb529971ef57932f
bash /home/check_git_changes.sh

yarn install || true

