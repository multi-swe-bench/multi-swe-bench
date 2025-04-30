#!/bin/bash
set -e

cd /home/simdjson
git reset --hard
bash /home/check_git_changes.sh
git checkout bf7834179c1f8fc523c9fd73d29b46348ae1d576
bash /home/check_git_changes.sh

mkdir build

