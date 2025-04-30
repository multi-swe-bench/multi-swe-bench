#!/bin/bash
set -e

cd /home/ponyc
git reset --hard
bash /home/check_git_changes.sh
git checkout e5398b7ab793e2b11f930aa375b9212887614b03
bash /home/check_git_changes.sh


