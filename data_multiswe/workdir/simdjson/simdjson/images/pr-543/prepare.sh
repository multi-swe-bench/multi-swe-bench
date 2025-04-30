#!/bin/bash
set -e

cd /home/simdjson
git reset --hard
bash /home/check_git_changes.sh
git checkout d140bc23f547e7cca43f85bf0ba1004e26e228e3
bash /home/check_git_changes.sh

mkdir build

