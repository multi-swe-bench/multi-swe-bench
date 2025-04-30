#!/bin/bash
set -e

cd /home/cli
go test -v -count=1 ./...

