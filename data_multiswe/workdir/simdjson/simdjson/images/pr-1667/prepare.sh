#!/bin/bash
set -e

cd /home/simdjson
git reset --hard
bash /home/check_git_changes.sh
git checkout 47a62db55936e29e1966a26a9aadb5f28237ae37
bash /home/check_git_changes.sh

mkdir build

