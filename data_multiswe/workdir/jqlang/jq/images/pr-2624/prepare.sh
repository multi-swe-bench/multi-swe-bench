#!/bin/bash
set -e

cd /home/jq
git reset --hard
bash /home/check_git_changes.sh
git checkout 9a590427db237d0aed5efe7eeaf13eb2bb3299d6
bash /home/check_git_changes.sh
git submodule update --init

