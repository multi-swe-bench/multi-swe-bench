# Copyright (c) 2024 Bytedance Ltd. and/or its affiliates

#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at

#      http://www.apache.org/licenses/LICENSE-2.0

#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

#!/bin/bash

# Check if a filename is provided as an argument
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <image list file>"
    exit 1
fi

# Read the filename
image_file="$1"

# Check if the file exists
if [ ! -f "$image_file" ]; then
    echo "File $image_file does not exist."
    exit 1
fi

# Read file line by line and download images
while IFS= read -r image; do
    # Skip empty lines
    if [ -z "$image" ]; then
        continue
    fi
    
    echo "Downloading image: $image"
    docker pull "$image"
done < "$image_file"

echo "All images have been downloaded."