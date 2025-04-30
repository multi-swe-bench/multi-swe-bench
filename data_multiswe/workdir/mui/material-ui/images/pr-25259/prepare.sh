#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout fe2632d1eb87f0b544be104aa89d06f6a2a64e23
bash /home/check_git_changes.sh

yarn install || true

