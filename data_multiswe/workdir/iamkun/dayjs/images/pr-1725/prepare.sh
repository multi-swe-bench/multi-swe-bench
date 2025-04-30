#!/bin/bash
set -e

cd /home/dayjs
git reset --hard
bash /home/check_git_changes.sh
git checkout 5a108ff3159c53fd270ea7638f33c35c934d6457
bash /home/check_git_changes.sh

npm uninstall rollup
npm install rollup@latest --save-dev

npm install --legacy-peer-deps || npm install --force || true
