#!/bin/bash
set -e

cd /home/dayjs
git reset --hard
bash /home/check_git_changes.sh
git checkout 5a465cc90c0ace55268b2640512d0a4c6544ac7f
bash /home/check_git_changes.sh

npm uninstall rollup
npm install rollup@latest --save-dev

npm install --legacy-peer-deps || npm install --force || true
