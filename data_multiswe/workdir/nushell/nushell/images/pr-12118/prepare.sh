#!/bin/bash
set -e

cd /home/nushell
git reset --hard
bash /home/check_git_changes.sh
git checkout f695ba408aec1b67cb51ed1aa1180721986b56d8
bash /home/check_git_changes.sh

cargo test || true

