#!/bin/bash
set -e

cd /home/json
git reset --hard
bash /home/check_git_changes.sh
git checkout b7be613b6ec6269c829144ff1cc8a633876d3092
bash /home/check_git_changes.sh

mkdir -p build
cp -r /home/json_test_data /home/json/build/

