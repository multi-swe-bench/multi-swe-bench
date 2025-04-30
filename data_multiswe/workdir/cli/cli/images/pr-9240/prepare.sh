#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 658f125ab365af7e442ddf58542cf47af1684a17
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

