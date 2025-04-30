#!/bin/bash
set -e

cd /home/zstd
git reset --hard
bash /home/check_git_changes.sh
git checkout c584e84e68109e6722e32cf0157a2c3706ca8f0d
bash /home/check_git_changes.sh

