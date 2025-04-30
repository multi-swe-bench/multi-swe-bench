#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout e59262926c473fa1f6356f3ad150a9ca82e4ae0c
bash /home/check_git_changes.sh

yarn install || true

