#!/bin/bash
set -e

cd /home/ponyc
git reset --hard
bash /home/check_git_changes.sh
git checkout a84d28a29ffd6a6c1a660d3fe1d0eb845d095d7b
bash /home/check_git_changes.sh


