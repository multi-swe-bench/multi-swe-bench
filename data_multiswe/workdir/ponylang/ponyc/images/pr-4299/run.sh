#!/bin/bash
set -e

cd /home/ponyc
make libs
make configure config=debug
make build config=debug
make test config=debug
