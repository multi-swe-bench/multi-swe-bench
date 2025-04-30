#!/bin/bash
set -e

cd /home/nushell
git reset --hard
bash /home/check_git_changes.sh
git checkout d68c3ec89a8efa304246467f80140c59467ba94f
bash /home/check_git_changes.sh

cargo test || true

