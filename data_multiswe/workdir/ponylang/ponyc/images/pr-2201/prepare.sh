#!/bin/bash
set -e

cd /home/ponyc
git reset --hard
bash /home/check_git_changes.sh
git checkout f00f95b30dd68c7faaff0aa88508c218bc19f02b
bash /home/check_git_changes.sh


    