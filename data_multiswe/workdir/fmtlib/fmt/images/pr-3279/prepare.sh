#!/bin/bash
set -e

cd /home/fmt
git reset --hard
bash /home/check_git_changes.sh
git checkout f89cd276f7dead38f11cebc73d1e91a1b1b38124
bash /home/check_git_changes.sh
mkdir build || true

