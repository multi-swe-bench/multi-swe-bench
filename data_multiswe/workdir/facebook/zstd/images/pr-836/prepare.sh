#!/bin/bash
set -e

cd /home/zstd
git reset --hard
bash /home/check_git_changes.sh
git checkout 3128e03be69b9d3db054a3765ae1310c7b3666f6
bash /home/check_git_changes.sh

