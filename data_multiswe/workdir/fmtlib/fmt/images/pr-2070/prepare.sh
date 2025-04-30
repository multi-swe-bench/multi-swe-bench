#!/bin/bash
set -e

cd /home/fmt
git reset --hard
bash /home/check_git_changes.sh
git checkout e737672614dfad3a6df23ffe3f2348fcfa4d3944
bash /home/check_git_changes.sh
mkdir build || true

