#!/bin/bash
set -e

cd /home/zstd
git reset --hard
bash /home/check_git_changes.sh
git checkout 1f25b17c7da7640cb3ce06f99e28b87811fddd26
bash /home/check_git_changes.sh

