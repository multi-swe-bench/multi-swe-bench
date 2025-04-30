#!/bin/bash
set -e

cd /home/jq
git reset --hard
bash /home/check_git_changes.sh
git checkout 0b558f6ed498717546406b5367483b976578a9b2
bash /home/check_git_changes.sh
git submodule update --init

