#!/bin/bash
set -e

cd /home/fmt
git reset --hard
bash /home/check_git_changes.sh
git checkout 275b4b3417e26be3bdb5b45e16fa9af6584973a2
bash /home/check_git_changes.sh
mkdir build || true

