#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout 5115f08e29babb11481a190d68e7fd045f3ce804
bash /home/check_git_changes.sh

yarn install || true

