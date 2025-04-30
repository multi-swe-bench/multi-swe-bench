#!/bin/bash
set -e

cd /home/nushell
git reset --hard
bash /home/check_git_changes.sh
git checkout 6f59abaf4310487f7a6319437be6ec61abcbc3b9
bash /home/check_git_changes.sh

cargo test || true

