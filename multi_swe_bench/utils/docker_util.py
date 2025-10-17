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

import logging
from pathlib import Path
from typing import Optional, Union

import docker

import docker.errors
import os
import tarfile
from pathlib import Path
import io

from docker.models.containers import Container

docker_client = docker.from_env()


def exists(image_name: str) -> bool:
    try:
        docker_client.images.get(image_name)
        return True
    except docker.errors.ImageNotFound:
        return False


def build(
    workdir: Path, dockerfile_name: str, image_full_name: str, logger: logging.Logger
):
    workdir = str(workdir)
    logger.info(
        f"Start building image `{image_full_name}`, working directory is `{workdir}`"
    )
    try:
        build_logs = docker_client.api.build(
            path=workdir,
            dockerfile=dockerfile_name,
            tag=image_full_name,
            rm=True,
            forcerm=True,
            decode=True,
            encoding="utf-8",
        )

        for log in build_logs:
            if "stream" in log:
                logger.info(log["stream"].strip())
            elif "error" in log:
                error_message = log["error"].strip()
                logger.error(f"Docker build error: {error_message}")
                raise RuntimeError(f"Docker build failed: {error_message}")
            elif "status" in log:
                logger.info(log["status"].strip())
            elif "aux" in log:
                logger.info(log["aux"].get("ID", "").strip())

        logger.info(f"image({workdir}) build success: {image_full_name}")
    except docker.errors.BuildError as e:
        logger.error(f"build error: {e}")
        raise e
    except Exception as e:
        logger.error(f"Unknown build error occurred: {e}")
        raise e


def run(
    image_full_name: str,
    run_command: str,
    output_path: Optional[Path] = None,
    global_env: Optional[list[str]] = None,
    volumes: Optional[Union[dict[str, str], list[str]]] = None,
) -> str:
    container = None
    try:
        container = docker_client.containers.create(
            image=image_full_name,
            command=run_command,
            detach=True,
            environment=global_env,
        )
        for source_file_path, target_file_info in volumes.items():
            file_content = Path(source_file_path).read_text()
            target_file_path = target_file_info["bind"]
            write_to_container(container, file_content, Path(target_file_path))
        container.start()
        output = ""
        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                for line in container.logs(stream=True, follow=True):
                    line_decoded = line.decode("utf-8")
                    f.write(line_decoded)
                    output += line_decoded
        else:
            container.wait()
            output = container.logs().decode("utf-8")
        return output
    finally:
        if container:
            try:
                container.remove(force=True)
            except Exception as e:
                print(f"Warning: Failed to remove container: {e}")


def copy_to_container(container: Container, src: Path, dst: Path):
    """
    Copy a file from local to a docker container

    Args:
        container (Container): Docker container to copy to
        src (Path): Source file path
        dst (Path): Destination file path in the container
    """
    # Check if destination path is valid
    if os.path.dirname(dst) == "":
        raise ValueError(
            f"Destination path parent directory cannot be empty!, dst: {dst}"
        )

    # temporary tar file
    tar_path = src.with_suffix(".tar")
    with tarfile.open(tar_path, "w") as tar:
        tar.add(
            src, arcname=dst.name
        )  # use destination name, so after `put_archive`, name is correct

    # get bytes for put_archive cmd
    with open(tar_path, "rb") as tar_file:
        data = tar_file.read()

    # Make directory if necessary
    container.exec_run(f"mkdir -p {dst.parent}")

    # Send tar file to container and extract
    container.put_archive(os.path.dirname(dst), data)

    # clean up in locally and in container
    tar_path.unlink()

def get_from_container(container: Container, src: Path, dst: Path):
    """
    Copy a file from a docker container to local
    Args:
        container (Container): Docker container to copy from
        src (Path): Source file path in the container
        dst (Path): Destination file path
    """
    # Check if destination path is valid
    if os.path.dirname(dst) == "":
        os.makedirs(dst.parent, exist_ok=True)
    stream, _ = container.get_archive(src)
    tar_buffer = io.BytesIO()
    for chunk in stream:
        tar_buffer.write(chunk)
    tar_buffer.seek(0)
    with tarfile.open(fileobj=tar_buffer) as tar:
        for member in tar.getmembers():
            if member.name == src.name:
                with open(dst, "wb") as f:
                    f.write(tar.extractfile(member).read())
                return
    raise FileNotFoundError(f"File {src} not found in container")

def read_from_container(container: Container, src: Path) -> str:
    """
    Read a file from a docker container and return its contents as a string
    """
    # get bytes for get_archive cmd
    stream, _ = container.get_archive(src)
    tar_buffer = io.BytesIO()
    for chunk in stream:
        tar_buffer.write(chunk)
    tar_buffer.seek(0)

    with tarfile.open(fileobj=tar_buffer) as tar:
        for member in tar.getmembers():
            if member.name == src.name:
                with tar.extractfile(member) as f:
                    return f.read().decode("utf-8")
    raise FileNotFoundError(f"File {src} not found in container")

def write_to_container(container: Container, data: str, dst: Path):
    """
    Write a string to a file in a docker container
    """
    data_bytes = data.encode('utf-8')
    stream = io.BytesIO()
    with tarfile.open(fileobj=stream, mode='w') as tar:
        tarinfo = tarfile.TarInfo(name=dst.name)
        tarinfo.size = len(data_bytes)
        tarinfo.mode = 0o644
        tar.addfile(tarinfo, io.BytesIO(data_bytes))
    
    stream.seek(0)
    container.put_archive(path=str(dst.parent), data=stream)
