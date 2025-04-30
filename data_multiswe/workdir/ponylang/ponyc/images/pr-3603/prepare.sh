#!/bin/bash
set -e

cd /home/ponyc
git reset --hard
bash /home/check_git_changes.sh
git checkout 0d5185441afd4fed1017430e7af89128969ebdc2
bash /home/check_git_changes.sh


