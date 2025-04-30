#!/bin/bash
set -e

cd /home/ponyc
git reset --hard
bash /home/check_git_changes.sh
git checkout eb6fbbb16600249e1d90cd3e6674ebe75fecc5b0
bash /home/check_git_changes.sh


