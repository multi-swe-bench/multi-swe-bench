#!/bin/bash
set -e

cd /home/simdjson
git reset --hard
bash /home/check_git_changes.sh
git checkout d4f4608dab2c70ceed233b818e1563581bc415a7
bash /home/check_git_changes.sh

mkdir build

