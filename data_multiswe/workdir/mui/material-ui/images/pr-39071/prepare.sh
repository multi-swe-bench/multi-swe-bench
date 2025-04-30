#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout ba4c5596cdbbdf07e78cb10ca7231db9968812db
bash /home/check_git_changes.sh

yarn install || true

