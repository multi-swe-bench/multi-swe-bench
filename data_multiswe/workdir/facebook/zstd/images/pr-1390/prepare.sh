#!/bin/bash
set -e

cd /home/zstd
git reset --hard
bash /home/check_git_changes.sh
git checkout e26126cacaa9ac6f1db4021ac3d32f4ac8387c50
bash /home/check_git_changes.sh

