#!/bin/bash
set -e

cd /home/zstd
git reset --hard
bash /home/check_git_changes.sh
git checkout a505463710aa34bccafd268c44064c129cdfb3e2
bash /home/check_git_changes.sh

