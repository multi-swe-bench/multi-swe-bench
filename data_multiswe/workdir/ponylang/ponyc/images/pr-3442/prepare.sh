#!/bin/bash
set -e

cd /home/ponyc
git reset --hard
bash /home/check_git_changes.sh
git checkout 764110c805d8020f5202c60ffed2b2570caf792a
bash /home/check_git_changes.sh


    