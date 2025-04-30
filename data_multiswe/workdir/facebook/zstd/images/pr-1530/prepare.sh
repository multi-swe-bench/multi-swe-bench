#!/bin/bash
set -e

cd /home/zstd
git reset --hard
bash /home/check_git_changes.sh
git checkout 54e9412ddd02ca4c6663d09dbf44f5a209a9a7ce
bash /home/check_git_changes.sh

