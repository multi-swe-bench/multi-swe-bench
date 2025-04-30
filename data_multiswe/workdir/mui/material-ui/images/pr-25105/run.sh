#!/bin/bash
set -e

cd /home/material-ui
yarn run test:unit --reporter json  --exit

