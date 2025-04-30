#!/bin/bash
set -e

cd /home/ponyc
git reset --hard
bash /home/check_git_changes.sh
git checkout df892a1903bcd053198290170aff3e05e348031a
bash /home/check_git_changes.sh


    