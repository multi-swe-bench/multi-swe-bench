#!/bin/bash
set -e

cd /home/Catch2
git reset --hard
bash /home/check_git_changes.sh
git checkout 2cb5210caf35bf8fc29ade2e5570cc0f37537951
bash /home/check_git_changes.sh

mkdir build

