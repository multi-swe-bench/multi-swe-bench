#!/bin/bash
set -e

cd /home/zstd
git reset --hard
bash /home/check_git_changes.sh
git checkout df09d4318f0f4f06d76c1e288732f5f9b1d9f59a
bash /home/check_git_changes.sh

