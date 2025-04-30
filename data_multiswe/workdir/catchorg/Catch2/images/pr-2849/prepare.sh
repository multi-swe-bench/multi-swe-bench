#!/bin/bash
set -e

cd /home/Catch2
git reset --hard
bash /home/check_git_changes.sh
git checkout 7ce35799767de7b9c6ba836c72e479c5f70219a3
bash /home/check_git_changes.sh

mkdir build

