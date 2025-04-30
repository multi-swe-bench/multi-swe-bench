#!/bin/bash
set -e

cd /home/cpp-httplib
git reset --hard
bash /home/check_git_changes.sh
git checkout 44b3fe6277398f424f1844295b7ae46ba5a1a35f
bash /home/check_git_changes.sh

