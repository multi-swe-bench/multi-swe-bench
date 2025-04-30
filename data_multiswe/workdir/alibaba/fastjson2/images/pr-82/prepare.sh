#!/bin/bash
set -e

cd /home/fastjson2
git config core.autocrlf input
git config core.filemode false
echo ".gitattributes" >> .git/info/exclude
echo "*.zip binary" >> .gitattributes
echo "*.png binary" >> .gitattributes
echo "*.jpg binary" >> .gitattributes
git add .
git reset --hard
bash /home/check_git_changes.sh
git checkout 3aed80608b36c310d0fe5f240f49d670b3638698
bash /home/check_git_changes.sh

./mvnw -V --no-transfer-progress -Pgen-javadoc -Pgen-dokka clean package -Dsurefire.useFile=false -Dmaven.test.skip=false -DfailIfNoTests=false || true

