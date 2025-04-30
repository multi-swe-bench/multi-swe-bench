#!/bin/bash
set -e

cd /home/axios
git reset --hard
bash /home/check_git_changes.sh
git checkout bc9af51b1886d1b3529617702f2a21a6c0ed5d92
bash /home/check_git_changes.sh

npm ci || true

