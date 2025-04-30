#!/bin/bash
set -e

cd /home/express
git reset --hard
bash /home/check_git_changes.sh
git checkout dc538f6e810bd462c98ee7e6aae24c64d4b1da93
bash /home/check_git_changes.sh

npm install || true

