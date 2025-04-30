#!/bin/bash
set -e

cd /home/material-ui
git apply /home/test.patch /home/fix.patch
yarn run test:unit --reporter json 

