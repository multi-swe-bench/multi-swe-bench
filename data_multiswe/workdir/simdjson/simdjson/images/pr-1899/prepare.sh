#!/bin/bash
set -e

cd /home/simdjson
git reset --hard
bash /home/check_git_changes.sh
git checkout 5809e51ae405d763700ec19083009a2a1cdbfdbc
bash /home/check_git_changes.sh

mkdir build

