#!/bin/bash
set -e

cd /home/dayjs
npm test -- --verbose && codecov 
