# Overview
<img src=".\image\Construction.png">
The process of building datasets is shown above (Phase1~4),
This demo is about how to build a dataset and participate in our Multi-SWE-RL community, includes the following phases:

1. `Repository Selection`
   * Selection of high-quality and well-maintained Repositories
2. `PR Crawling`
   * Crawling PR dataset with `get_pipeline.py` 
3. `Environment Determinaton`
   * Configure the execution environment for your collected dataset.
   * Verify your dataset can be run while parsing the logs.
4. `PR Filters and Generates Final Data (Jsonl)`
   * Filtering of final dataset based on generated reports and parsed logs.
5. `Submitting PRs to Huggingface `
   * Upload your new dataset to our Multi-SWE-RL Community.
6. `Submitting PRs to Github `
   * Upload the code you changed in stages 3 ~ 4 to github
7. `Tracking Progress`

**Notes**: 
* Your newly created dataset **can't overlap with the dataset we've already released**.
* Record the license when using open source repositories, and provide the relevant license if it's your own private repo (a license of your own design or an open source license)

If you want to know about the specifics of how each phase works,what follows will be a step-by-step guide.

# 1.Repository Selection

On GitHub, you can filter repositories based on specific conditions. For example, if you want to find repositories that primarily use C++, you can use the following search query:

```
language:C++
```
Additionally, you can further refine your search based on criteria such as the number of stars or pull requests. For instance, if you want to find repositories that primarily use C++ and have more than 100 stars, you can use:

```
language:C++ stars:>100
```
On the GitHub search results page, there is a sorting option in the top-right corner that allows you to organize the results based on different criteria, such as:

- Best match (Default sorting based on relevance)

- Most stars (Sort by the number of stars to find the most popular repositories)

- Most forks (Sort by the number of forks to find the most widely adopted repositories)

- Recently updated (Sort by the most recently updated repositories to find active projects)

By using these filtering and sorting options, you can quickly find repositories that meet your needs.

<img src="image\select_repo.png">


# 2.PR Crawling

**Note**: Before you start the next steps, you need to fork our repository and clone it locally.

Make sure you have [installed](../README.md#install-from-source) our repository. If you want to collect pull requests (PRs) from the repository `catchorg/Catch2` and have created an output directory, such as `collect/catchorg__Catch2`, you can execute the following command:

```bash
python -m multi_swe_bench.collect.get_pipeline \
    --out_dir collect/catchorg__Catch2 \
    --org catchorg \
    --repo Catch2 \
    --tokens <your_github_tokens>    # GitHub tokens
```
After execution, the generated files will be:
```
collect/catchorg__Catch2/
    ├── catchorg__Catch2_prs.jsonl             
    ├── catchorg__Catch2_filtered_prs.jsonl    
    ├── catchorg__Catch2_related_issues.jsonl  
    └── catchorg__Catch2_dataset.jsonl 
```
The most important file is `catchorg__Catch2_dataset.jsonl`, which contains the instances for execution environment determinaton.

# 3.Environment Determinaton

This is the most challenging but crucial step. We need to configure the execution environment for the collected `catchorg/Catch2` instances using Docker.

Since `catchorg/Catch2` is a C++ repository, we first need to create a folder inside `multi_swe_bench/harness/repos/cpp`. It is recommended to name the folder after the repository's organization (catchorg). Inside this folder, create two new files:

- A Python file for handling repository execution (recommended to use the repository name, `catch2.py`).

- An `__init__.py` file for package initialization.

The resulting directory structure should be as follows:

```
multi_swe_bench/harness/repos/cpp/
    ├── catchorg/             
        ├── catch2.py    
        └── __init__.py
    └── __init__.py
```
**Note**: When naming files, it is recommended to use lowercase letters and remove special characters such as `-` and `_`. If multiple repositories share the same organization, their execution files can be placed in the same organization folder and managed through `__init__.py`.

## Updating the __init__.py Files
After creating the files, update the `__init__.py` file in `multi_swe_bench/harness/repos/cpp` to include:

```
from multi_swe_bench.harness.repos.cpp.catchorg import *
```
Similarly, update `multi_swe_bench/harness/repos/cpp/catchorg/__init__.py` with:
```
from multi_swe_bench.harness.repos.cpp.catchorg.catch2 import *
```
## Implementing catch2.py
Next, we need to implement `catch2.py`, which is responsible for configuring the Base Image, Instance Image, and running the Instance. This is achieved through three types of classes:

- **Class for configuring the Base Image**: These classes set up the basic environment with necessary dependencies and the code repository.

- **Class for configuring the Instance Image**: This class configures the Instance Image, which is tailored for each PR and contains the required scripts for execution.

- **Class for running the Instance**: This class manages the execution process, applies various scripts, and parses the results.


### Class for configuring the Base Image
The first type configures the Base Image and can be named `Catch2ImageBase`. Below is an explanation of this class with code examples:
```python
class Catch2ImageBase(Image):
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
        return "gcc:latest"

    def image_name(self) -> str:
        return f"{self.pr.org}/{self.pr.repo}".lower()

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

        return f"""FROM {image_name}

{self.global_env}

WORKDIR /home/

{code}
RUN apt-get update && apt-get install -y \
    libbrotli-dev \
    libcurl4-openssl-dev \
    clang \
    build-essential \
    cmake \
    python3 \
    python3-dev \
    python3-pip

{self.clear_env}

"""
```
The `dependency` method in this class returns the dependency image for the Base Image. For example:

```
def dependency(self) -> Union[str, "Image"]:
   return "gcc:latest"
```
This specifies `gcc:latest` as the base dependency image.

The `image_tag` and `workdir` methods define the image tag and the directory name for storing the image, usually set to the same value.

The most critical part of this class is the `dockerfile` method, as shown below:
```python
    def dockerfile(self) -> str:
        image_name = self.dependency()
        if isinstance(image_name, Image):
            image_name = image_name.image_full_name()

        if self.config.need_clone:
            code = f"RUN git clone https://github.com/{self.pr.org}/{self.pr.repo}.git /home/{self.pr.repo}"
        else:
            code = f"COPY {self.pr.repo} /home/{self.pr.repo}"

        return f"""FROM {image_name}

{self.global_env}

WORKDIR /home/

{code}
RUN apt-get update && apt-get install -y \
    libbrotli-dev \
    libcurl4-openssl-dev \
    clang \
    build-essential \
    cmake \
    python3 \
    python3-dev \
    python3-pip

{self.clear_env}

"""
```
The `dockerfile` method returns the generated Dockerfile content, where:

- `{image_name}` is specified by the `dependency` method.

- `{self.global_env}` and `{self.clear_env}` represent proxy configuration commands.

- `{code}` represents the repository cloning process.

To set up the base environment for the repository, we need to include installation commands in the Dockerfile. The following snippet demonstrates how to install essential packages:

```
RUN apt-get update && apt-get install -y \
    libbrotli-dev \
    libcurl4-openssl-dev \
    clang \
    build-essential \
    cmake \
    python3 \
    python3-dev \
    python3-pip
```
To determine the necessary packages, you can refer to the repository’s GitHub homepage, such as `.github/workflows`, `README.md`, etc. Additionally, you can look at execution files from other repositories in our project for inspiration. This is a challenging but essential task.

### Class for configuring the Instance Image
The second type of class is responsible for configuring the Instance Image. This class can be named `Catch2ImageDefault`. Below is an explanation with code examples:
```python
class Catch2ImageDefault(Image):
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
        return Catch2ImageBase(self.pr, self._config)

    def image_name(self) -> str:
        return f"{self.pr.org}/{self.pr.repo}".lower()

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

""".format(
                    pr=self.pr
                ),
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

""".format(
                    pr=self.pr
                ),
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
set -e

cd /home/{pr.repo}
cd build
cmake -DCATCH_DEVELOPMENT_BUILD=ON ..
make
ctest
""".format(
                    pr=self.pr
                ),
            ),
            File(
                ".",
                "test-run.sh",
                """#!/bin/bash
set -e

cd /home/{pr.repo}
git apply --whitespace=nowarn /home/test.patch
cd build
cmake -DCATCH_DEVELOPMENT_BUILD=ON ..
make
ctest

""".format(
                    pr=self.pr
                ),
            ),
            File(
                ".",
                "fix-run.sh",
                """#!/bin/bash
set -e

cd /home/{pr.repo}
git apply --whitespace=nowarn /home/test.patch /home/fix.patch
cd build
cmake -DCATCH_DEVELOPMENT_BUILD=ON ..
make
ctest

""".format(
                    pr=self.pr
                ),
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
```
The `dependency` method in this class returns the required Base Image. For example:

```
def dependency(self) -> Image | None:
    return Catch2ImageBase(self.pr, self._config)
```
Here, we directly return the previously defined `Catch2ImageBase`.

Similar to the Base Image class, the `image_tag` and `workdir` methods define the image tag and the directory name for storing the image, usually set to the same value.

The `file` method is crucial in configuring the Instance Image. It specifies the files included in the image, such as:

- `fix.patch` (gold patch file)

- `test.patch` (test patch file)

- `check_git_changes.sh` (script to check for git changes)

- `prepare.sh` (preparation script before running)

- `run.sh` (script for running without applying any test or gold patches)

- `test-run.sh` (script for running after applying the test patch)

- `fix-run.sh` (script for running after applying both test and gold patches)


To run an instance, the most critical scripts to modify are `prepare.sh`, `run.sh`, `test-run.sh`, and `fix-run.sh`.

`prepare.sh`: This script performs initial setup tasks before executing the main scripts. It can be used to switch branches, create the build directory, etc., so these operations do not need to be repeated in other scripts.

```python
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
""".format(
        pr=self.pr
    )
)
```

`run.sh`: This script navigates to the repository, enters the build folder, runs CMake and Make for compilation, and finally executes tests using CTest.

```python
File(
    ".",
    "run.sh",
    """#!/bin/bash
set -e

cd /home/{pr.repo}
cd build
cmake -DCATCH_DEVELOPMENT_BUILD=ON ..
make
ctest
""".format(
        pr=self.pr
    )
)
```

`test-run.sh`: Compared to `run.sh`, this script includes an additional step to apply the test patch before running the tests.

```python
File(
    ".",
    "test-run.sh",
    """#!/bin/bash
set -e

cd /home/{pr.repo}
git apply --whitespace=nowarn /home/test.patch
cd build
cmake -DCATCH_DEVELOPMENT_BUILD=ON ..
make
ctest

""".format(
        pr=self.pr
    )
)
```
`fix-run.sh`: Compared to `test-run.sh`, this script includes an extra step to apply the gold patch.

```python
File(
    ".",
    "fix-run.sh",
    """#!/bin/bash
set -e

cd /home/{pr.repo}
git apply --whitespace=nowarn /home/fix.patch
cd build
cmake -DCATCH_DEVELOPMENT_BUILD=ON ..
make
ctest

""".format(
        pr=self.pr
    )
)
```
The `dockerfile` method in this class returns the Dockerfile content for the Instance Image. The main tasks include:

- Specifying the base image.

- Configuring proxy settings.

- Copying necessary files.

- Running `prepare.sh`.

- Clearing proxy settings.

Generally, this method does not require modifications.

### Class for running the Instance
The final class is responsible for running the Instance, which is defined as follows:

```python
@Instance.register("catchorg", "Catch2")
class Catch2(Instance):
    def __init__(self, pr: PullRequest, config: Config, *args, **kwargs):
        super().__init__()
        self._pr = pr
        self._config = config

    @property
    def pr(self) -> PullRequest:
        return self._pr

    def dependency(self) -> Optional[Image]:
        return Catch2ImageDefault(self.pr, self._config)

    def run(self) -> str:
        return "bash /home/run.sh"

    def test_patch_run(self) -> str:
        return "bash /home/test-run.sh"

    def fix_patch_run(self) -> str:
        return "bash /home/fix-run.sh"

    def parse_log(self, test_log: str) -> TestResult:
        passed_tests = set()
        failed_tests = set()
        skipped_tests = set()

        return TestResult(
            passed_count=len(passed_tests),
            failed_count=len(failed_tests),
            skipped_count=len(skipped_tests),
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            skipped_tests=skipped_tests,
        )
```
In this class, we need to register the repository. The project will locate the corresponding files based on the instance's org and repo. Therefore, we must configure:

```
@Instance.register("catchorg", "Catch2")
```
The most crucial part of this class is defining the `parse_log` method. This method is responsible for parsing the logs and extracting test cases and their statuses. The statuses are generally categorized into three types:

- passed (successful test)

- failed (failed test)

- skipped (skipped test)

Since `parse_log` depends on logs from running instances, we can initially keep the three test case sets empty.
A complete version will be implemented [later](#Implementing-parse_log).
## Running the Collected Instances
Now, let's run the collected instances based on the configured files. Before running the instances, we need to create three directories:

- work (working directory)

- output (output directory)

- repos (repository directory)

After setting them up, the directory structure will look like this:

```
multi_swe_bench/
├── collect/   
├── multi_swe_bench/           
├── output/
├── repos/ 
└── work/ 
```

If you need to use a proxy, configure the proxy address. You can execute the following command:
```
python multi_swe_bench\harness\build_dataset.py \
    --workdir work \
    --raw_dataset_files collect/catchorg__Catch2/catchorg__Catch2_dataset.jsonl \ 
    --log_dir work \ 
    --output_dir output \ 
    --repo_dir repos \ 
    --need_clone true \
    --global_env \
    HTTP_PROXY=http://host.docker.internal:7890 \
    http_proxy=http://host.docker.internal:7890 \
    HTTPS_PROXY=http://host.docker.internal:7890 \
    https_proxy=http://host.docker.internal:7890
```
After successful running, you will see the generated images and log files in the `work` directory, and the results in the `output` directory.
```
multi_swe_bench/
├── collect/   
├── multi_swe_bench/           
├── output/
    ├── catchorg__Catch2_dataset.jsonl
    └── final_report.json
├── repos/
    └── catchorg/
└──  work/ 
    └── catchorg/Catch2/
        ├── images/
        └── instances/
            ├── pr-xxxx
                ├── fix-patch-run.log
                ├── report.log
                ├── run.log
                └── test-patch-run.log
            └── ...
```
## Implementing `parse_log`
We can read the log files generated in the `work` directory and extract all test cases using regular expressions. For this repository, the `parse_log` implementation is as follows:
```python
    def parse_log(self, test_log: str) -> TestResult:
        passed_tests = set()
        failed_tests = set()
        skipped_tests = set()

        re_passes = [
            re.compile(r"^-- Performing Test (.+) - Success$", re.IGNORECASE),
            re.compile(
                r"^\d+/\d+ Test\s+#\d+: (.+) \.+\s+ Passed\s+.+$", re.IGNORECASE
            ),
        ]
        re_fails = [
            re.compile(r"^-- Performing Test (.+) - Failed$", re.IGNORECASE),
            re.compile(
                r"^\d+/\d+ Test\s+#\d+: (.+) \.+\*\*\*Failed\s+.+$", re.IGNORECASE
            ),
        ]
        re_skips = [
            re.compile(r"^-- Performing Test (.+) - skipped$", re.IGNORECASE),
        ]

        for line in test_log.splitlines():
            line = line.strip().lower()
            if not line:
                continue

            for re_pass in re_passes:
                pass_match = re_pass.match(line)
                if pass_match:
                    test = pass_match.group(1)
                    passed_tests.add(test)

            for re_fail in re_fails:
                fail_match = re_fail.match(line)
                if fail_match:
                    test = fail_match.group(1)
                    failed_tests.add(test)

            for re_skip in re_skips:
                skip_match = re_skip.match(line)
                if skip_match:
                    test = skip_match.group(1)
                    skipped_tests.add(test)

        return TestResult(
            passed_count=len(passed_tests),
            failed_count=len(failed_tests),
            skipped_count=len(skipped_tests),
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            skipped_tests=skipped_tests,
        )
```

## Debugging Errors
If errors occur in the logs, debugging is necessary. For example, the above configuration might cause an error when running the instance for PR #2554. 
You can analyze the logs to identify the error, or you can reference the base commit (`base.sha: 8ce92d2c7288b6b3261caf1c016f8a779b6a8efc`) for this instance to check the repository state at [that commit](https://github.com/catchorg/Catch2/tree/8ce92d2c7288b6b3261caf1c016f8a779b6a8efc).

Upon investigation, the error may be related to the gcc version. 
Since dependency installation is determined by the Base image, we can redefine a new Base image configuration class, such as `Catch2ImageBaseCpp12`:
```python
class Catch2ImageBaseCpp12(Image):
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
        return "gcc:12"

    def image_name(self) -> str:
        return f"{self.pr.org}/{self.pr.repo}".lower()

    def image_tag(self) -> str:
        return "base-cpp-12"

    def workdir(self) -> str:
        return "base-cpp-12"

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

        return f"""FROM {image_name}

{self.global_env}

WORKDIR /home/

{code}
RUN apt-get update && apt-get install -y \
    libbrotli-dev \
    libcurl4-openssl-dev \
    clang \
    build-essential \
    cmake \
    python3 \
    python3-dev \
    python3-pip

{self.clear_env}

"""
```
In the `Catch2ImageDefault` class, we can modify the dependency image for specific instances. The simplest way is to modify the `dependency` method based on the PR number:
```
def dependency(self) -> Image | None:
    if self.pr.number and self.pr.number <= 2554:
        return Catch2ImageBaseCpp12(self.pr, self._config)
    return Catch2ImageBase(self.pr, self._config)
```

Due to version changes, previous configurations often become invalid. In such cases, we can flexibly:
- Create a new class to configure the Base Image and modify the `dependency` method in `Catch2ImageDefault`.
- Adjust the `file` method in `Catch2ImageDefault`.

We have already demonstrated the first approach. The second approach is necessary when test commands vary across versions, as seen in [bitcoin's configuration](../multi_swe_bench/harness/repos/cpp/bitcoin/bitcoin.py).
In this way, by continuously iterating and modifying, you can maximize the execution of all collected instances. The final modified file is similar to [Catch2](../multi_swe_bench/harness/repos/cpp/catchorg/catch2.py).

# 4.PR Filters and Generates Final Data (Jsonl)

Congratulations! You have completed the most challenging step. Now, you can filter qualified instances from the execution data. A qualified instance must fix failed tests with the golden patch and not introduce new issues.

The filtering process is based on `test-patch-run.log` and `fix-patch-run.log`, ensuring:

- There exist test cases that failed in `test-patch-run.log` but passed in `fix-patch-run.log`.

- No test cases that passed in `test-patch-run.log` failed in `fix-patch-run.log` due to the golden patch.

We provide an automated parsing method. When you execute:
```
python multi_swe_bench\harness\gen_report.py \
    --mode dataset \
    --workdir work \
    --raw_dataset_files collect/catchorg__Catch2/catchorg__Catch2_dataset.jsonl \ 
    --log_dir work \ 
    --output_dir output \ 
    --log_level DEBUG \ 
    --regen true 
```
It will invoke the `log_parse` method (configured in [Step 3](#Implementing-parse_log)) to analyze the execution logs, automatically extract failed and successful test cases for evaluation, and generate `final_report.json` and `catchorg__Catch2_dataset.jsonl` in the `output` directory. The filtered data is stored in `catchorg__Catch2_dataset.jsonl`, while `final_report.json` provides an overview of the dataset construction process.

# 5.Submitting PRs to Huggingface

This step is the beginning of a simple and enjoyable contribution process！

First you need to get into our [Multi-SWE-RL Huggingface Community](https://huggingface.co/datasets/bytedance-research/Multi-SWE-RL) 

**Notes:**This is a dataset repository that we will continue to maintain and update, and is currently scheduled to be updated every three months, with a separate file created for each update.

The file structure of this Multi-SWE-RL Huggingface repository is shown below：

```
data_20240601_20250331/
├── c/
    ├── org1__repo1_dataset.jsonl
    ├── org2__repo2_dataset.jsonl
    └── ...
├── cpp/
    ├── org3__repo3_dataset.jsonl
    ├── org4__repo4_dataset.jsonl
    └── ...
├── java/
    ├── ...
    └── ...
├── js/
    ├── ...
    └── ...
└── ...
data_20250401_20250631/
├── ...
└── ...
```

The contribution process is very simple and does not require the use of commands and code, please follow the steps below:

1. Go to the **Data folder** **with the latest date**, and go to the folder of the **contributed language**, and click **Upload files**.

   For example, if we want to contribute **catchorg__Catch2_dataset.jsonl** in **C++**, we will go to the folder with **the latest date** and click **Upload files**.


2. Then **upload** your catchorg__Catch2_dataset.jsonl, and then **add specific information about the dataset**, and then click **Open a Pull Request** to complete the PR submission!

At this point, congratulations on your huggingface PR submission!

# 6.Submitting PRs to Github

Fork our github repository, **submit the code changes of phase 1-4 as PR**, when submitting PR, you should **read the PR template carefully and fill in the relevant content**, such as huggingface link and specific data information and so on.

Refer specifically to the following sample PR for submitting a new dataset：https://github.com/multi-swe-bench/multi-swe-bench/pull/1



# 7.Tracking Progress

Next you just need to follow up on our reviews，We've created [Multi-SWE-RL Contribution Progress Board](https://docs.google.com/spreadsheets/d/1C90SiRmlac3FizmsJzxzrhSNsnCjyYewdrXzFbBV4x0/edit?gid=0#gid=0) to make it easy to track the Progress.

In addition to **recording the states of the data review**, this dashboard also **associates github PR and huggingface PR**, as well as recording **specific dataset information** for the current PR.

The data review has the following three states：

* `pending review：`The PR has gone through our PR format review (in this case including huggingface's PR correlation with github's PR, etc.) and is in the awaiting data review stage
* `needs to be fixed：`There is a issue in the data review stage that needs to be fixed, and we will respond to the specific issue in the discussion forum of the corresponding PR.
* `merged：`Congratulations, the new dataset you produced has been merged into the Multi-SWE-RL community!

We will review the PRs on the [Multi-SWE-RL Contribution Progress Board](https://docs.google.com/spreadsheets/d/1C90SiRmlac3FizmsJzxzrhSNsnCjyYewdrXzFbBV4x0/edit?gid=0#gid=0) **every three months**，

If you have any questions about the process, you can also join our [Discord](https://discord.gg/EtfbkfqUuN) to discuss it!

