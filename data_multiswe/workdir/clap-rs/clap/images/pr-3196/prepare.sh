#!/bin/bash
set -e

cd /home/clap
git reset --hard
bash /home/check_git_changes.sh
git checkout 27893cfd9a4dec68c54720dd540ab217112d6f54
bash /home/check_git_changes.sh

cargo test || true

