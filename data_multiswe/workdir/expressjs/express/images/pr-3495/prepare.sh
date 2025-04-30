#!/bin/bash
set -e

cd /home/express
git reset --hard
bash /home/check_git_changes.sh
git checkout 8da51108e7bb501344c537d3f1f846a7477ae329
bash /home/check_git_changes.sh

npm install || true

