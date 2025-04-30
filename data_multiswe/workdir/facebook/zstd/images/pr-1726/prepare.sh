#!/bin/bash
set -e

cd /home/zstd
git reset --hard
bash /home/check_git_changes.sh
git checkout c9072ee674c9a928281286022f4d9393b0d113ec
bash /home/check_git_changes.sh

