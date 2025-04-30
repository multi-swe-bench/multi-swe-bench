#!/bin/bash
set -e

cd /home/zstd
git reset --hard
bash /home/check_git_changes.sh
git checkout 919d1d8e93809327687ec34502cf4cf50573598e
bash /home/check_git_changes.sh

