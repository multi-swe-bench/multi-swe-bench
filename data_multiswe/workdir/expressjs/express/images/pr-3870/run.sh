#!/bin/bash
set -e

cd /home/express
npm run test-ci -- --reporter json
