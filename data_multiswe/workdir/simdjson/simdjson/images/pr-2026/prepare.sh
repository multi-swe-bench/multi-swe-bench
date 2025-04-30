#!/bin/bash
set -e

cd /home/simdjson
git reset --hard
bash /home/check_git_changes.sh
git checkout c5c43e9c7ff613bf01ca14b9b9083d38a6efd5fc
bash /home/check_git_changes.sh

mkdir build

