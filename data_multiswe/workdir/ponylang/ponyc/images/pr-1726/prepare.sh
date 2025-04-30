#!/bin/bash
set -e

cd /home/ponyc
git reset --hard
bash /home/check_git_changes.sh
git checkout c995c4674b9ef062fa74b38be52682f945007dd2
bash /home/check_git_changes.sh


    