#!/bin/bash
set -e

cd /home/Catch2
git reset --hard
bash /home/check_git_changes.sh
git checkout 65c9a1d31a338f28ef93cd61c475efc40f6cc42e
bash /home/check_git_changes.sh

mkdir build

