#!/bin/bash
set -e

cd /home/zstd
git reset --hard
bash /home/check_git_changes.sh
git checkout 517d8c984ce9b30792fe5b6c8c79547d3748f34d
bash /home/check_git_changes.sh

