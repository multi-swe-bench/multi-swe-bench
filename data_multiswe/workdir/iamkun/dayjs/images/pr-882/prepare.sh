#!/bin/bash
set -e

cd /home/dayjs
git reset --hard
bash /home/check_git_changes.sh
git checkout bcea06730da2d19ddbad844de3557ee077af821c
bash /home/check_git_changes.sh

npm uninstall rollup
npm install rollup@latest --save-dev

npm install --legacy-peer-deps || npm install --force || true
