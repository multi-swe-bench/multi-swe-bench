#!/bin/bash
set -e

cd /home/ponyc
git reset --hard
bash /home/check_git_changes.sh
git checkout 336000f438564ca2863d32685964ccd23ec9d174
bash /home/check_git_changes.sh


    