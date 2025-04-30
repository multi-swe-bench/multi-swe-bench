#!/bin/bash
set -e

cd /home/jq
git reset --hard
bash /home/check_git_changes.sh
git checkout 6944d81bc874da1ada15cbb340d020b32f9f90bd
bash /home/check_git_changes.sh
git submodule update --init

