#!/bin/bash
set -e

cd /home/bat
git reset --hard
bash /home/check_git_changes.sh
git checkout e1a3fc5529d55abc73aa5fb18368d22f9b9bb71c
bash /home/check_git_changes.sh

cargo test || true

