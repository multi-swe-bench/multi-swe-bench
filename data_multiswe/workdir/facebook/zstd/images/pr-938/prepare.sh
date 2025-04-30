#!/bin/bash
set -e

cd /home/zstd
git reset --hard
bash /home/check_git_changes.sh
git checkout b3d76e0a94502e2f484d7495c88ca3a21d44155b
bash /home/check_git_changes.sh

