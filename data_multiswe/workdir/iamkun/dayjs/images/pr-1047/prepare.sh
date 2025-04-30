#!/bin/bash
set -e

cd /home/dayjs
git reset --hard
bash /home/check_git_changes.sh
git checkout cdc49a1911c74b7ea96ed222f42796d53715cfed
bash /home/check_git_changes.sh

npm uninstall rollup
npm install rollup@latest --save-dev

npm install --legacy-peer-deps || npm install --force || true
