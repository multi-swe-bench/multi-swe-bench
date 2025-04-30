#!/bin/bash
set -e

cd /home/fmt
git reset --hard
bash /home/check_git_changes.sh
git checkout 7612f18dc8e0112e64e0845a1ebe9da6cfb8a123
bash /home/check_git_changes.sh
mkdir build || true

