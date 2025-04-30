#!/bin/bash
set -e

cd /home/dayjs
git reset --hard
bash /home/check_git_changes.sh
git checkout f4cb2cfd77246116cb4151c74ca2f600a17cd951
bash /home/check_git_changes.sh

npm uninstall rollup
npm install rollup@latest --save-dev

npm install --legacy-peer-deps || npm install --force || true
