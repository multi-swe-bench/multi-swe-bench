#!/bin/bash
set -e

cd /home/Catch2
git reset --hard
bash /home/check_git_changes.sh
git checkout 00347f1e79260e76d5072cca5b3636868397dda5
bash /home/check_git_changes.sh

mkdir build

