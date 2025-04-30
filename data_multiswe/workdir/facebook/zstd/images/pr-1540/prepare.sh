#!/bin/bash
set -e

cd /home/zstd
git reset --hard
bash /home/check_git_changes.sh
git checkout be3bd70c57a23383401f8a883cdecaca1d10a4d7
bash /home/check_git_changes.sh

