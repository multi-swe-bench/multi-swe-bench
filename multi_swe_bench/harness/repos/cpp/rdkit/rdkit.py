import re
from typing import Optional, Union

from multi_swe_bench.harness.image import Config, File, Image
from multi_swe_bench.harness.instance import Instance, TestResult
from multi_swe_bench.harness.pull_request import PullRequest



class RDKitImageBase_gt_5130_lt_6300(Image):
    def __init__(self, pr: PullRequest, config: Config):
        self._pr = pr
        self._config = config

    @property
    def pr(self) -> PullRequest:
        return self._pr

    @property
    def config(self) -> Config:
        return self._config

    def dependency(self) -> Union[str, "Image"]:
        return "ubuntu:24.04"

    def image_tag(self) -> str:
        return "base"

    def workdir(self) -> str:
        return "base"

    def files(self) -> list[File]:
        return []

    def dockerfile(self) -> str:

        image_name = self.dependency()
        if isinstance(image_name, Image):
            image_name = image_name.image_full_name()
        
        if self.config.need_clone:
            code = f"RUN git clone https://github.com/{self.pr.org}/{self.pr.repo}.git /home/{self.pr.repo}"
        else:
            code = f"COPY {self.pr.repo} /home/{self.pr.repo}"

        template = """
FROM {image_name}

{global_env}

WORKDIR /home/

# 基础依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    git vim python3-cairo python3-pil wget bzip2 ca-certificates \
    build-essential cmake pkg-config python3-dev python3-numpy \
 && rm -rf /var/lib/apt/lists/*

# 安装 Miniconda
ENV CONDA_DIR=/opt/conda
RUN wget -q https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /tmp/miniconda.sh \
 && bash /tmp/miniconda.sh -b -p $CONDA_DIR \
 && rm -f /tmp/miniconda.sh
ENV PATH=$CONDA_DIR/bin:$PATH

# 创建 conda 环境：切到 gcc/g++ 12 工具链（conda-forge），带 ninja/cmake/boost/eigen 等
RUN conda config --system --set channel_priority strict \
 && conda create -y -n rdkit-dev -c conda-forge --override-channels \
    python=3.11 \
    gcc_linux-64=12.* gxx_linux-64=12.* gfortran_linux-64=12.* \
    cmake ninja eigen cairo pillow numpy pandas freetype pkg-config \
    boost-cpp=1.82 libboost-python=1.82 \
 && conda clean -afy

# 默认使用 rdkit-dev 环境的可执行文件/库；并指明编译器（gcc/g++ 12）
ENV PATH=/opt/conda/envs/rdkit-dev/bin:$PATH \
    LD_LIBRARY_PATH=/opt/conda/envs/rdkit-dev/lib:$LD_LIBRARY_PATH \
    CC=x86_64-conda-linux-gnu-gcc \
    CXX=x86_64-conda-linux-gnu-g++ \
    CMAKE_PREFIX_PATH=/opt/conda/envs/rdkit-dev \
    CMAKE_GENERATOR=Ninja

SHELL ["bash", "-lc"]
# 可选：交互进入时自动激活（对 RUN 层一般没影响，但保留也不碍事）
RUN echo "source /opt/conda/etc/profile.d/conda.sh" >> /root/.bashrc && \
    echo "conda activate rdkit-dev" >> /root/.bashrc

{code}

{clear_env}
        """
        
        file_text = template.format(
            image_name=image_name,
            global_env=self.global_env,
            code=code,
            clear_env=self.clear_env,
        )
        
        return file_text


class RDKitImageDefault_gt_3000_lt_5130(Image):
    def __init__(self, pr: PullRequest, config: Config):
        self._pr = pr
        self._config = config

    @property
    def pr(self) -> PullRequest:
        return self._pr

    @property
    def config(self) -> Config:
        return self._config

    def dependency(self) -> Image | None:
        return RDKitImageBase_gt_5130_lt_6300(self.pr, self._config)  # base image还是使用 gt_5130_lt_6300 的。

    def image_tag(self) -> str:
        return f"pr-{self.pr.number}"

    def workdir(self) -> str:
        return f"pr-{self.pr.number}"

    def files(self) -> list[File]:

        return [
            File(
                ".",
                "fix.patch",
                f"{self.pr.fix_patch}",
            ),
            File(
                ".",
                "test.patch",
                f"{self.pr.test_patch}",
            ),
            File(
                ".",
                "check_git_changes.sh",
                """#!/bin/bash
set -e

if ! git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
  echo "check_git_changes: Not inside a git repository"
  exit 1
fi

if [[ -n $(git status --porcelain) ]]; then
  echo "check_git_changes: Uncommitted changes"
  exit 1
fi

echo "check_git_changes: No uncommitted changes"
exit 0

""".format(),
            ),
            File(
                ".",
                "prepare.sh",
                """#!/bin/bash
set -e

cd /home/{pr.repo}
git reset --hard
bash /home/check_git_changes.sh
git checkout {pr.base.sha}
bash /home/check_git_changes.sh

mkdir build

""".format(pr=self.pr),
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
set -e

cd /home/{pr.repo}

# —— 自动补上缺失的静态成员定义（幂等）——
if [ -f Code/GraphMol/FileParsers/testMultithreadedMolSupplier.cpp ]; then
  grep -q 'PrintThread::cout_mutex' Code/GraphMol/FileParsers/testMultithreadedMolSupplier.cpp || \
    printf '\n// auto-added for missing out-of-class definition\nstd::mutex PrintThread::cout_mutex;\n' \
    >> Code/GraphMol/FileParsers/testMultithreadedMolSupplier.cpp
fi


mkdir -p build
cd build

conda run -n rdkit-dev cmake .. \
  -DRDK_BUILD_TESTS=ON \
  -DRDK_BUILD_PYTHON_WRAPPERS=OFF \
  -DRDK_BUILD_MOLDRAW2D=OFF \
  -DRDK_INSTALL_COMIC_FONTS=OFF \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_C_FLAGS="-DCATCH_CONFIG_NO_POSIX_SIGNALS" \
  -DCMAKE_CXX_FLAGS="-DCATCH_CONFIG_NO_POSIX_SIGNALS"

conda run -n rdkit-dev cmake --build . --target all -j"$(nproc)"

export RDBASE=/home/rdkit
ctest --output-on-failure

""".format(pr=self.pr),
            ),
            File(
                ".",
                "test-run.sh",
                """#!/bin/bash
set -e

cd /home/{pr.repo}

# —— 自动补上缺失的静态成员定义（幂等）——
if [ -f Code/GraphMol/FileParsers/testMultithreadedMolSupplier.cpp ]; then
  grep -q 'PrintThread::cout_mutex' Code/GraphMol/FileParsers/testMultithreadedMolSupplier.cpp || \
    printf '\n// auto-added for missing out-of-class definition\nstd::mutex PrintThread::cout_mutex;\n' \
    >> Code/GraphMol/FileParsers/testMultithreadedMolSupplier.cpp
fi


git apply --whitespace=nowarn /home/test.patch
cd build

conda run -n rdkit-dev cmake .. \
  -DRDK_BUILD_TESTS=ON \
  -DRDK_BUILD_PYTHON_WRAPPERS=OFF \
  -DRDK_BUILD_MOLDRAW2D=OFF \
  -DRDK_INSTALL_COMIC_FONTS=OFF \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_C_FLAGS="-DCATCH_CONFIG_NO_POSIX_SIGNALS" \
  -DCMAKE_CXX_FLAGS="-DCATCH_CONFIG_NO_POSIX_SIGNALS"

conda run -n rdkit-dev cmake --build . --target all -j"$(nproc)"

export RDBASE=/home/rdkit
ctest --output-on-failure

""".format(pr=self.pr),
            ),
            File(
                ".",
                "fix-run.sh",
                """#!/bin/bash
set -e

cd /home/{pr.repo}

# —— 自动补上缺失的静态成员定义（幂等）——
if [ -f Code/GraphMol/FileParsers/testMultithreadedMolSupplier.cpp ]; then
  grep -q 'PrintThread::cout_mutex' Code/GraphMol/FileParsers/testMultithreadedMolSupplier.cpp || \
    printf '\n// auto-added for missing out-of-class definition\nstd::mutex PrintThread::cout_mutex;\n' \
    >> Code/GraphMol/FileParsers/testMultithreadedMolSupplier.cpp
fi

git apply --whitespace=nowarn /home/test.patch /home/fix.patch
cd build

conda run -n rdkit-dev cmake .. \
  -DRDK_BUILD_TESTS=ON \
  -DRDK_BUILD_PYTHON_WRAPPERS=OFF \
  -DRDK_BUILD_MOLDRAW2D=OFF \
  -DRDK_INSTALL_COMIC_FONTS=OFF \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_C_FLAGS="-DCATCH_CONFIG_NO_POSIX_SIGNALS" \
  -DCMAKE_CXX_FLAGS="-DCATCH_CONFIG_NO_POSIX_SIGNALS"

conda run -n rdkit-dev cmake --build . --target all -j"$(nproc)"

export RDBASE=/home/rdkit
ctest --output-on-failure

""".format(pr=self.pr),
            ),
        ]

    def dockerfile(self) -> str:
        image = self.dependency()
        name = image.image_name()
        tag = image.image_tag()

        copy_commands = ""
        for file in self.files():
            copy_commands += f"COPY {file.name} /home/\n"

        prepare_commands = "RUN bash /home/prepare.sh"

        return f"""FROM {name}:{tag}

{self.global_env}

{copy_commands}

{prepare_commands}

{self.clear_env}

"""



class RDKitImageDefault_gt_5130_lt_6300(Image):
    def __init__(self, pr: PullRequest, config: Config):
        self._pr = pr
        self._config = config

    @property
    def pr(self) -> PullRequest:
        return self._pr

    @property
    def config(self) -> Config:
        return self._config

    def dependency(self) -> Image | None:
        return RDKitImageBase_gt_5130_lt_6300(self.pr, self._config)

    def image_tag(self) -> str:
        return f"pr-{self.pr.number}"

    def workdir(self) -> str:
        return f"pr-{self.pr.number}"

    def files(self) -> list[File]:

        return [
            File(
                ".",
                "fix.patch",
                f"{self.pr.fix_patch}",
            ),
            File(
                ".",
                "test.patch",
                f"{self.pr.test_patch}",
            ),
            File(
                ".",
                "check_git_changes.sh",
                """#!/bin/bash
set -e

if ! git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
  echo "check_git_changes: Not inside a git repository"
  exit 1
fi

if [[ -n $(git status --porcelain) ]]; then
  echo "check_git_changes: Uncommitted changes"
  exit 1
fi

echo "check_git_changes: No uncommitted changes"
exit 0

""".format(),
            ),
            File(
                ".",
                "prepare.sh",
                """#!/bin/bash
set -e

cd /home/{pr.repo}
git reset --hard
bash /home/check_git_changes.sh
git checkout {pr.base.sha}
bash /home/check_git_changes.sh

mkdir build

""".format(pr=self.pr),
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
set -e

cd /home/{pr.repo}

mkdir -p build
cd build

conda run -n rdkit-dev cmake .. -DRDK_BUILD_PYTHON_WRAPPERS=OFF -DRDK_BUILD_MOLDRAW2D=OFF -DRDK_INSTALL_COMIC_FONTS=OFF
conda run -n rdkit-dev cmake --build . --target all -j"$(nproc)"

export RDBASE=/home/rdkit
ctest --output-on-failure

""".format(pr=self.pr),
            ),
            File(
                ".",
                "test-run.sh",
                """#!/bin/bash
set -e

cd /home/{pr.repo}
git apply --whitespace=nowarn /home/test.patch
cd build

conda run -n rdkit-dev cmake .. -DRDK_BUILD_PYTHON_WRAPPERS=OFF -DRDK_BUILD_MOLDRAW2D=OFF -DRDK_INSTALL_COMIC_FONTS=OFF
conda run -n rdkit-dev cmake --build . --target all -j"$(nproc)"

export RDBASE=/home/rdkit
ctest --output-on-failure

""".format(pr=self.pr),
            ),
            File(
                ".",
                "fix-run.sh",
                """#!/bin/bash
set -e

cd /home/{pr.repo}
git apply --whitespace=nowarn /home/test.patch /home/fix.patch
cd build

conda run -n rdkit-dev cmake .. -DRDK_BUILD_PYTHON_WRAPPERS=OFF -DRDK_BUILD_MOLDRAW2D=OFF -DRDK_INSTALL_COMIC_FONTS=OFF
conda run -n rdkit-dev cmake --build . --target all -j"$(nproc)"

export RDBASE=/home/rdkit
ctest --output-on-failure

""".format(pr=self.pr),
            ),
        ]

    def dockerfile(self) -> str:
        image = self.dependency()
        name = image.image_name()
        tag = image.image_tag()

        copy_commands = ""
        for file in self.files():
            copy_commands += f"COPY {file.name} /home/\n"

        prepare_commands = "RUN bash /home/prepare.sh"

        return f"""FROM {name}:{tag}

{self.global_env}

{copy_commands}

{prepare_commands}

{self.clear_env}

"""








class RDKitImageBase(Image):
    def __init__(self, pr: PullRequest, config: Config):
        self._pr = pr
        self._config = config

    @property
    def pr(self) -> PullRequest:
        return self._pr

    @property
    def config(self) -> Config:
        return self._config

    def dependency(self) -> Union[str, "Image"]:
        return "ubuntu:24.04"

    def image_tag(self) -> str:
        return "base"

    def workdir(self) -> str:
        return "base"

    def files(self) -> list[File]:
        return []

    def dockerfile(self) -> str:

        image_name = self.dependency()
        if isinstance(image_name, Image):
            image_name = image_name.image_full_name()
        
        if self.config.need_clone:
            code = f"RUN git clone https://github.com/{self.pr.org}/{self.pr.repo}.git /home/{self.pr.repo}"
        else:
            code = f"COPY {self.pr.repo} /home/{self.pr.repo}"

        template = """
FROM {image_name}

{global_env}

WORKDIR /home/

RUN apt-get update && apt-get install -y --no-install-recommends \\
    git vim python3-cairo python3-pil wget bzip2 ca-certificates \\
    build-essential cmake pkg-config python3-dev python3-numpy \\
&& rm -rf /var/lib/apt/lists/*

# 安装 Miniconda
ENV CONDA_DIR=/opt/conda
RUN wget -q https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /tmp/miniconda.sh \\
&& bash /tmp/miniconda.sh -b -p ${{CONDA_DIR}} \\
&& rm -f /tmp/miniconda.sh
ENV PATH=${{CONDA_DIR}}/bin:${{PATH}}

# 创建 conda 环境（包含 libboost-python=1.82）
RUN conda config --system --set channel_priority strict \\
&& conda create -y -n rdkit-dev -c conda-forge --override-channels \\
    python=3.11 cmake eigen boost-cpp=1.82 libboost-python=1.82 \\
    cairo pillow numpy pandas freetype pkg-config ninja \\
&& conda clean -afy

# 默认让后续 RUN 使用 rdkit-dev 的可执行文件/库
ENV PATH=/opt/conda/envs/rdkit-dev/bin:${{PATH}}
ENV LD_LIBRARY_PATH=/opt/conda/envs/rdkit-dev/lib:${{LD_LIBRARY_PATH}}

SHELL ["bash", "-lc"]
RUN echo "source /opt/conda/etc/profile.d/conda.sh" >> /root/.bashrc && \\
    echo "conda activate rdkit-dev" >> /root/.bashrc

{code}

{clear_env}
        """
        
        file_text = template.format(
            image_name=image_name,
            global_env=self.global_env,
            code=code,
            clear_env=self.clear_env,
        )
        
        return file_text



class RDKitImageBase_gt_7300(Image):
    def __init__(self, pr: PullRequest, config: Config):
        self._pr = pr
        self._config = config

    @property
    def pr(self) -> PullRequest:
        return self._pr

    @property
    def config(self) -> Config:
        return self._config

    def dependency(self) -> Union[str, "Image"]:
        return "ubuntu:24.04"

    def image_tag(self) -> str:
        return "base"

    def workdir(self) -> str:
        return "base"

    def files(self) -> list[File]:
        return []

    def dockerfile(self) -> str:

        image_name = self.dependency()
        if isinstance(image_name, Image):
            image_name = image_name.image_full_name()
        
        if self.config.need_clone:
            code = f"RUN git clone https://github.com/{self.pr.org}/{self.pr.repo}.git /home/{self.pr.repo}"
        else:
            code = f"COPY {self.pr.repo} /home/{self.pr.repo}"

        template = """
FROM {image_name}

{global_env}

WORKDIR /home/

RUN apt-get update && apt-get install -y --no-install-recommends \\
    git vim python3-cairo python3-pil wget bzip2 ca-certificates \\
    build-essential cmake pkg-config python3-dev python3-numpy \\
&& rm -rf /var/lib/apt/lists/*

# 安装 Miniconda
ENV CONDA_DIR=/opt/conda
RUN wget -q https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /tmp/miniconda.sh \\
&& bash /tmp/miniconda.sh -b -p ${{CONDA_DIR}} \\
&& rm -f /tmp/miniconda.sh
ENV PATH=${{CONDA_DIR}}/bin:${{PATH}}

# 创建 conda 环境（包含 libboost-python=1.85）
RUN conda config --system --set channel_priority strict \\
&& conda create -y -n rdkit-dev -c conda-forge --override-channels \\
    python=3.11 cmake eigen boost-cpp=1.85 libboost-python=1.85 \\
    cairo pillow numpy pandas freetype pkg-config ninja \\
&& conda clean -afy

# 默认让后续 RUN 使用 rdkit-dev 的可执行文件/库
ENV PATH=/opt/conda/envs/rdkit-dev/bin:${{PATH}}
ENV LD_LIBRARY_PATH=/opt/conda/envs/rdkit-dev/lib:${{LD_LIBRARY_PATH}}

SHELL ["bash", "-lc"]
RUN echo "source /opt/conda/etc/profile.d/conda.sh" >> /root/.bashrc && \\
    echo "conda activate rdkit-dev" >> /root/.bashrc

{code}

{clear_env}
        """
        
        file_text = template.format(
            image_name=image_name,
            global_env=self.global_env,
            code=code,
            clear_env=self.clear_env,
        )
        
        return file_text


class RDKitImageDefault_gt_7300(Image):
    def __init__(self, pr: PullRequest, config: Config):
        self._pr = pr
        self._config = config

    @property
    def pr(self) -> PullRequest:
        return self._pr

    @property
    def config(self) -> Config:
        return self._config

    def dependency(self) -> Image | None:
        return RDKitImageBase_gt_7300(self.pr, self._config)

    def image_tag(self) -> str:
        return f"pr-{self.pr.number}"

    def workdir(self) -> str:
        return f"pr-{self.pr.number}"

    def files(self) -> list[File]:

        return [
            File(
                ".",
                "fix.patch",
                f"{self.pr.fix_patch}",
            ),
            File(
                ".",
                "test.patch",
                f"{self.pr.test_patch}",
            ),
            File(
                ".",
                "check_git_changes.sh",
                """#!/bin/bash
set -e

if ! git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
  echo "check_git_changes: Not inside a git repository"
  exit 1
fi

if [[ -n $(git status --porcelain) ]]; then
  echo "check_git_changes: Uncommitted changes"
  exit 1
fi

echo "check_git_changes: No uncommitted changes"
exit 0

""".format(),
            ),
            File(
                ".",
                "prepare.sh",
                """#!/bin/bash
set -e

cd /home/{pr.repo}
git reset --hard
bash /home/check_git_changes.sh
git checkout {pr.base.sha}
bash /home/check_git_changes.sh

mkdir build

""".format(pr=self.pr),
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
set -e

cd /home/{pr.repo}

mkdir -p build
cd build

conda run -n rdkit-dev cmake .. -DRDK_BUILD_PYTHON_WRAPPERS=OFF
conda run -n rdkit-dev cmake --build . --target all -j"$(nproc)"

export RDBASE=/home/rdkit
ctest --output-on-failure

""".format(pr=self.pr),
            ),
            File(
                ".",
                "test-run.sh",
                """#!/bin/bash
set -e

cd /home/{pr.repo}
git apply --whitespace=nowarn /home/test.patch
cd build

conda run -n rdkit-dev cmake .. -DRDK_BUILD_PYTHON_WRAPPERS=OFF
conda run -n rdkit-dev cmake --build . --target all -j"$(nproc)"

export RDBASE=/home/rdkit
ctest --output-on-failure

""".format(pr=self.pr),
            ),
            File(
                ".",
                "fix-run.sh",
                """#!/bin/bash
set -e

cd /home/{pr.repo}
git apply --whitespace=nowarn /home/test.patch /home/fix.patch
cd build

conda run -n rdkit-dev cmake .. -DRDK_BUILD_PYTHON_WRAPPERS=OFF
conda run -n rdkit-dev cmake --build . --target all -j"$(nproc)"

export RDBASE=/home/rdkit
ctest --output-on-failure

""".format(pr=self.pr),
            ),
        ]

    def dockerfile(self) -> str:
        image = self.dependency()
        name = image.image_name()
        tag = image.image_tag()

        copy_commands = ""
        for file in self.files():
            copy_commands += f"COPY {file.name} /home/\n"

        prepare_commands = "RUN bash /home/prepare.sh"

        return f"""FROM {name}:{tag}

{self.global_env}

{copy_commands}

{prepare_commands}

{self.clear_env}

"""




class RDKitImageDefault(Image):
    def __init__(self, pr: PullRequest, config: Config):
        self._pr = pr
        self._config = config

    @property
    def pr(self) -> PullRequest:
        return self._pr

    @property
    def config(self) -> Config:
        return self._config

    def dependency(self) -> Image | None:
        return RDKitImageBase(self.pr, self._config)

    def image_tag(self) -> str:
        return f"pr-{self.pr.number}"

    def workdir(self) -> str:
        return f"pr-{self.pr.number}"

    def files(self) -> list[File]:


        return [
            File(
                ".",
                "fix.patch",
                f"{self.pr.fix_patch}",
            ),
            File(
                ".",
                "test.patch",
                f"{self.pr.test_patch}",
            ),
            File(
                ".",
                "check_git_changes.sh",
                """#!/bin/bash
set -e

if ! git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
  echo "check_git_changes: Not inside a git repository"
  exit 1
fi

if [[ -n $(git status --porcelain) ]]; then
  echo "check_git_changes: Uncommitted changes"
  exit 1
fi

echo "check_git_changes: No uncommitted changes"
exit 0

""".format(),
            ),
            File(
                ".",
                "prepare.sh",
                """#!/bin/bash
set -e

cd /home/{pr.repo}
git reset --hard
bash /home/check_git_changes.sh
git checkout {pr.base.sha}
bash /home/check_git_changes.sh

mkdir build

""".format(pr=self.pr),
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
set -e

cd /home/{pr.repo}

mkdir -p build
cd build

conda run -n rdkit-dev cmake .. -DRDK_BUILD_PYTHON_WRAPPERS=OFF -DRDK_BUILD_MOLDRAW2D=OFF -DRDK_INSTALL_COMIC_FONTS=OFF
conda run -n rdkit-dev cmake --build . --target all -j"$(nproc)"

export RDBASE=/home/rdkit
ctest --output-on-failure

""".format(pr=self.pr),
            ),
            File(
                ".",
                "test-run.sh",
                """#!/bin/bash
set -e

cd /home/{pr.repo}
git apply --whitespace=nowarn /home/test.patch
cd build

conda run -n rdkit-dev cmake .. -DRDK_BUILD_PYTHON_WRAPPERS=OFF -DRDK_BUILD_MOLDRAW2D=OFF -DRDK_INSTALL_COMIC_FONTS=OFF
conda run -n rdkit-dev cmake --build . --target all -j"$(nproc)"

export RDBASE=/home/rdkit
ctest --output-on-failure

""".format(pr=self.pr),
            ),
            File(
                ".",
                "fix-run.sh",
                """#!/bin/bash
set -e

cd /home/{pr.repo}
git apply --whitespace=nowarn /home/test.patch /home/fix.patch
cd build

conda run -n rdkit-dev cmake .. -DRDK_BUILD_PYTHON_WRAPPERS=OFF -DRDK_BUILD_MOLDRAW2D=OFF -DRDK_INSTALL_COMIC_FONTS=OFF
conda run -n rdkit-dev cmake --build . --target all -j"$(nproc)"

export RDBASE=/home/rdkit
ctest --output-on-failure

""".format(pr=self.pr),
            ),
        ]

    def dockerfile(self) -> str:
        image = self.dependency()
        name = image.image_name()
        tag = image.image_tag()

        copy_commands = ""
        for file in self.files():
            copy_commands += f"COPY {file.name} /home/\n"

        prepare_commands = "RUN bash /home/prepare.sh"

        return f"""FROM {name}:{tag}

{self.global_env}

{copy_commands}

{prepare_commands}

{self.clear_env}

"""



@Instance.register("rdkit", "rdkit")
class RDkit(Instance):
    def __init__(self, pr: PullRequest, config: Config, *args, **kwargs):
        super().__init__()
        self._pr = pr
        self._config = config

    @property
    def pr(self) -> PullRequest:
        return self._pr


    def dependency(self) -> Image | None:
        if  7300<= self.pr.number:
            return RDKitImageDefault_gt_7300(self.pr, self._config)
        elif self.pr.number < 6300 and self.pr.number >= 5130:
            return RDKitImageDefault_gt_5130_lt_6300(self.pr, self._config)
        elif self.pr.number < 5130 and self.pr.number >= 3000:
            return RDKitImageDefault_gt_3000_lt_5130(self.pr, self._config)
        return RDKitImageDefault(self.pr, self._config)

    def run(self, run_cmd: str = "") -> str:
        if run_cmd:
            return run_cmd
        return "bash /home/run.sh"

    def test_patch_run(self, test_patch_run_cmd: str = "") -> str:
        if test_patch_run_cmd:
            return test_patch_run_cmd

        return "bash /home/test-run.sh"

    def fix_patch_run(self, fix_patch_run_cmd: str = "") -> str:
        if fix_patch_run_cmd:
            return fix_patch_run_cmd

        return "bash /home/fix-run.sh"

    def parse_log(self, test_log: str) -> TestResult:
        passed_tests = set()
        failed_tests = set()
        skipped_tests = set()

        re_pass_tests = [re.compile(r"^\d+/\d+\s*Test\s*#\d+:\s*(.*?)\s*\.+\s*Passed")]
        re_fail_tests = [
            re.compile(r"^\d+/\d+\s*Test\s*#\d+:\s*(.*?)\s*\.+\s*\*+Failed$")
        ]

        for line in test_log.splitlines():
            line = line.strip()
            if not line:
                continue

            for re_pass_test in re_pass_tests:
                pass_match = re_pass_test.match(line)
                if pass_match:
                    test = pass_match.group(1)
                    passed_tests.add(test)

            for re_fail_test in re_fail_tests:
                fail_match = re_fail_test.match(line)
                if fail_match:
                    test = fail_match.group(1)
                    failed_tests.add(test)

        return TestResult(
            passed_count=len(passed_tests),
            failed_count=len(failed_tests),
            skipped_count=len(skipped_tests),
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            skipped_tests=skipped_tests,
        )
