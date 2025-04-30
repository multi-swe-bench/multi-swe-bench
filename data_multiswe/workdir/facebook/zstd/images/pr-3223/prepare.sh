#!/bin/bash
set -e

cd /home/zstd
git reset --hard
bash /home/check_git_changes.sh
git checkout d0dcc9d775789af73f44accb318579465ccdada4
bash /home/check_git_changes.sh

