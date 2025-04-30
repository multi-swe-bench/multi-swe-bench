#!/bin/bash
set -e

cd /home/Catch2
git reset --hard
bash /home/check_git_changes.sh
git checkout 1faccd601d904a951142d8fba82914a8325b764e
bash /home/check_git_changes.sh

mkdir build

