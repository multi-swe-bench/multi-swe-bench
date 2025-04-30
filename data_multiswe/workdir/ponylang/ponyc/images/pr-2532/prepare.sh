#!/bin/bash
set -e

cd /home/ponyc
git reset --hard
bash /home/check_git_changes.sh
git checkout d34dce667accf0797f0afcc5e04fd0605d1ad82e
bash /home/check_git_changes.sh


    