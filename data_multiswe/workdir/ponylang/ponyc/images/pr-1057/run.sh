#!/bin/bash
set -e

cd /home/ponyc
make
make test
    