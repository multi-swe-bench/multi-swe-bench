#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout 1b24a942f93a07a7f2073942c6dec91bdd688d75
bash /home/check_git_changes.sh

yarn install || true

