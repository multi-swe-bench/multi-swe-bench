#!/bin/bash
set -e

cd /home/Catch2
git reset --hard
bash /home/check_git_changes.sh
git checkout 1a8a793178d50b74b0f9a0adb3eec937b61039a9
bash /home/check_git_changes.sh

mkdir build

