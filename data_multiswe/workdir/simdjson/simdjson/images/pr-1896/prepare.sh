#!/bin/bash
set -e

cd /home/simdjson
git reset --hard
bash /home/check_git_changes.sh
git checkout d4ac1b51d0aeb2d4f792136fe7792de709006afa
bash /home/check_git_changes.sh

mkdir build

