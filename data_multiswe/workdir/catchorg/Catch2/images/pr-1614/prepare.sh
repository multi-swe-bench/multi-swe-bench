#!/bin/bash
set -e

cd /home/Catch2
git reset --hard
bash /home/check_git_changes.sh
git checkout 9c741fe96073ed620ffc032afbed1f3c789d2b68
bash /home/check_git_changes.sh

mkdir build

