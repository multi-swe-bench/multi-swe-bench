#!/bin/bash
set -e

cd /home/fmt
git reset --hard
bash /home/check_git_changes.sh
git checkout ccea338070c795fd966a4dc08b19268b6fbad5ef
bash /home/check_git_changes.sh
mkdir build || true

