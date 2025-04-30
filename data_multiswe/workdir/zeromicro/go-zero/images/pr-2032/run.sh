#!/bin/bash
set -e

cd /home/go-zero
go test -v -count=1 ./...

