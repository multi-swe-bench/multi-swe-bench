#!/bin/bash
set -e

cd /home/fmt
git reset --hard
bash /home/check_git_changes.sh
git checkout 2caf1b3b91f6d56f420cec8bf752f9af26aa51af
bash /home/check_git_changes.sh
mkdir build || true

