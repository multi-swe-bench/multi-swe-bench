#!/bin/bash
set -e

cd /home/clap
git apply /home/test.patch
cargo test

