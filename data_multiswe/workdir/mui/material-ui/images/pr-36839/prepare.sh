#!/bin/bash
set -e

cd /home/material-ui
git reset --hard
bash /home/check_git_changes.sh
git checkout 511b38515faa7766405cec114ffeda3b2077a4fc
bash /home/check_git_changes.sh

yarn install || true

