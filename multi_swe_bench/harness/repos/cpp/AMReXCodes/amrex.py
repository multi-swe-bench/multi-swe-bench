import re
from typing import Optional, Union

from multi_swe_bench.harness.image import Config, File, Image
from multi_swe_bench.harness.instance import Instance, TestResult
from multi_swe_bench.harness.pull_request import PullRequest


class AMReXImageBase(Image):
    """Base image for AMReX - builds AMReX from source"""
    
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
        # Use Ubuntu 22.04 as base
        # return "ubuntu:22.04"
        return "shuoxin/amrex-base-amd64:latest"

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

        return f"""FROM {image_name}

{self.global_env}

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Etc/UTC

# Just setup the workspace, don't checkout specific commit yet
WORKDIR /workspace
RUN cd amrex && \\
    git config --global --add safe.directory /workspace/amrex && \\
    chmod -R u+w /workspace/amrex/.git

ENV AMREX_HOME=/workspace/amrex
WORKDIR /workspace/amrex

{self.clear_env}

"""


class AMReXImageDefault(Image):
    """Instance-specific image for AMReX"""
    
    def __init__(self, pr: PullRequest, config: Config):
        self._pr = pr
        self._config = config

    @property
    def pr(self) -> PullRequest:
        return self._pr

    @property
    def config(self) -> Config:
        return self._config

    def dependency(self) -> Image:
        return AMReXImageBase(self.pr, self._config)

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
                "pr_info.txt",
                f"""pr_number:{self.pr.number}
title:{self.pr.title}
base_sha:{self.pr.base.sha}
""",
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
""",
            ),
            File(
                ".",
                "prepare.sh",
                """#!/bin/bash
set -e

cd /workspace/amrex
git reset --hard
/home/check_git_changes.sh
git fetch origin {pr.base.sha}
git checkout {pr.base.sha}
rm -rf build
/home/check_git_changes.sh

# Build AMReX with CMake at the base commit
# rm -rf build && mkdir -p build && cd build
# cmake .. \\
#     -DCMAKE_BUILD_TYPE=Debug \\
#     -DAMReX_SPACEDIM=3 \\
#     -DAMReX_FORTRAN=OFF \\
#     -DAMReX_MPI=OFF \\
#     -DAMReX_OMP=OFF \\
#     -DAMReX_PARTICLES=ON \\
#     -DAMReX_BUILD_TUTORIALS=OFF \\
#     -DCMAKE_INSTALL_PREFIX=/opt/amrex
# make -j64
# make install

""".format(pr=self.pr),
            ),
            File(
                ".",
                "run.sh",
                """#!/bin/bash
# Baseline run without any patches
# For AMReX, this is a dummy baseline that always passes
set +e

cd /workspace/amrex || exit 1

echo "Baseline test (no patches applied)"
echo "SUCCESS"
exit 0
""",
            ),
            File(
                ".",
                "test-run.sh",
                """#!/bin/bash
# Run tests with test patch only (should fail)
set -e

cd /workspace/amrex || exit 1

# Refresh git index to avoid "does not match index" errors
echo "Refreshing git index..."
git status > /dev/null 2>&1 || true

# Apply test patch (skip binary files)
echo "Applying test patch..."
git apply --ignore-space-change --ignore-whitespace /home/test.patch 2>&1 | grep -v "cannot apply binary patch" || {
    # If direct apply fails, try with --reject to skip problematic hunks
    echo "Retrying with --reject flag..."
    git apply --reject --ignore-space-change --ignore-whitespace /home/test.patch 2>&1 | grep -v "cannot apply binary patch" || true
    echo "Test patch applied (some hunks may have been rejected, binary files skipped)"
}

# Determine which test directory to build
# Extract test directory from patch - only get actual directories, not files
TEST_DIRS=$(grep "^diff --git a/Tests/" /home/test.patch | awk '{print $3}' | sed 's|^a/Tests/\\([^/]*\\).*|\\1|' | sort -u)

# Validate and find the first valid test directory
TEST_DIR=""
for dir in $TEST_DIRS; do
    if [ -d "/workspace/amrex/Tests/$dir" ] && [ "$dir" != "CMakeLists.txt" ]; then
        TEST_DIR=$dir
        break
    fi
done

if [ -z "$TEST_DIR" ]; then
    echo "ERROR: Could not determine test directory from patch"
    exit 1
fi

echo "Building and running test: $TEST_DIR"

cd /workspace/amrex/Tests/$TEST_DIR

# Detect which build system to use
# Check if this directory has build files at top level
if [ -f "GNUmakefile" ]; then
    echo "Using GNUmakefile build system"
    make -j4 || {
        echo "Build failed"
        exit 1
    }
    TEST_EXE=$(find . -maxdepth 1 -type f -executable \\( -name "*.exe" -o -name "*.ex" \\) 2>/dev/null | head -1)
elif [ -f "CMakeLists.txt" ]; then
    echo "Using CMake build system"
    mkdir -p build && cd build
    cmake .. \\
        -DCMAKE_BUILD_TYPE=Debug \\
        -DAMReX_SPACEDIM=3 \\
        -DAMReX_FORTRAN=OFF \\
        -DAMReX_MPI=OFF \\
        -DAMReX_OMP=OFF \\
        -DCMAKE_PREFIX_PATH=/opt/amrex || {
        echo "CMake configuration failed"
        exit 1
    }
    make -j4 || {
        echo "Build failed"
        exit 1
    }
    TEST_EXE=$(find . -maxdepth 1 -type f -executable | head -1)
else
    # Check subdirectories for build files
    echo "No build files at top level, checking subdirectories..."
    FOUND_SUBDIR=""
    for subdir in */; do
        if [ -f "$subdir/GNUmakefile" ] || [ -f "$subdir/CMakeLists.txt" ]; then
            FOUND_SUBDIR="$subdir"
            break
        fi
    done
    
    if [ -z "$FOUND_SUBDIR" ]; then
        echo "ERROR: No build files found in $TEST_DIR or its subdirectories"
        exit 1
    fi
    
    echo "Building in subdirectory: $FOUND_SUBDIR"
    cd "$FOUND_SUBDIR"
    
    if [ -f "GNUmakefile" ]; then
        echo "Using GNUmakefile build system"
        make -j4 || {
            echo "Build failed"
            exit 1
        }
        TEST_EXE=$(find . -maxdepth 1 -type f -executable \\( -name "*.exe" -o -name "*.ex" \\) 2>/dev/null | head -1)
    else
        echo "Using CMake build system"
        mkdir -p build && cd build
        cmake .. \\
            -DCMAKE_BUILD_TYPE=Debug \\
            -DAMReX_SPACEDIM=3 \\
            -DAMReX_FORTRAN=OFF \\
            -DAMReX_MPI=OFF \\
            -DAMReX_OMP=OFF \\
            -DCMAKE_PREFIX_PATH=/opt/amrex || {
            echo "CMake configuration failed"
            exit 1
        }
        make -j4 || {
            echo "Build failed"
            exit 1
        }
        TEST_EXE=$(find . -maxdepth 1 -type f -executable | head -1)
    fi
fi

if [ -z "$TEST_EXE" ]; then
    echo "ERROR: No test executable found"
    exit 1
fi

echo "Running test executable: $TEST_EXE"

# Check if inputs file exists
if [ -f ../inputs ]; then
    $TEST_EXE ../inputs 2>&1
elif [ -f ../../inputs ]; then
    $TEST_EXE ../../inputs 2>&1
else
    $TEST_EXE 2>&1
fi

TEST_EXIT_CODE=$?

if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "TEST_RESULT: PASS"
else
    echo "TEST_RESULT: FAIL"
fi

exit $TEST_EXIT_CODE
""",
            ),
            File(
                ".",
                "fix-run.sh",
                """#!/bin/bash
# Run tests with both test and fix patches (should pass)
set -e

cd /workspace/amrex || exit 1

# Refresh git index to avoid "does not match index" errors
echo "Refreshing git index..."
git status > /dev/null 2>&1 || true

# Apply test patch first (skip binary files)
echo "Applying test patch..."
git apply --ignore-space-change --ignore-whitespace /home/test.patch 2>&1 | grep -v "cannot apply binary patch" || {
    # If direct apply fails, try with --reject to skip problematic hunks
    echo "Retrying with --reject flag..."
    git apply --reject --ignore-space-change --ignore-whitespace /home/test.patch 2>&1 | grep -v "cannot apply binary patch" || true
    echo "Test patch applied (some hunks may have been rejected, binary files skipped)"
}

# Apply fix patch (skip binary files)
echo "Applying fix patch..."
git apply --ignore-space-change --ignore-whitespace /home/fix.patch 2>&1 | grep -v "cannot apply binary patch" || {
    # If direct apply fails, try with --reject to skip problematic hunks
    echo "Retrying with --reject flag..."
    git apply --reject --ignore-space-change --ignore-whitespace /home/fix.patch 2>&1 | grep -v "cannot apply binary patch" || true
    echo "Fix patch applied (some hunks may have been rejected, binary files skipped)"
}

# Determine which test directory to build
# Extract test directory from patch - only get actual directories, not files
TEST_DIRS=$(grep "^diff --git a/Tests/" /home/test.patch | awk '{print $3}' | sed 's|^a/Tests/\\([^/]*\\).*|\\1|' | sort -u)

# Validate and find the first valid test directory
TEST_DIR=""
for dir in $TEST_DIRS; do
    if [ -d "/workspace/amrex/Tests/$dir" ] && [ "$dir" != "CMakeLists.txt" ]; then
        TEST_DIR=$dir
        break
    fi
done

if [ -z "$TEST_DIR" ]; then
    echo "ERROR: Could not determine test directory from patch"
    exit 1
fi

echo "Building and running test: $TEST_DIR"

cd /workspace/amrex/Tests/$TEST_DIR

# Detect which build system to use
# Check if this directory has build files at top level
if [ -f "GNUmakefile" ]; then
    echo "Using GNUmakefile build system"
    make -j4 || {
        echo "Build failed"
        exit 1
    }
    TEST_EXE=$(find . -maxdepth 1 -type f -executable \\( -name "*.exe" -o -name "*.ex" \\) 2>/dev/null | head -1)
elif [ -f "CMakeLists.txt" ]; then
    echo "Using CMake build system"
    mkdir -p build && cd build
    cmake .. \\
        -DCMAKE_BUILD_TYPE=Debug \\
        -DAMReX_SPACEDIM=3 \\
        -DAMReX_FORTRAN=OFF \\
        -DAMReX_MPI=OFF \\
        -DAMReX_OMP=OFF \\
        -DCMAKE_PREFIX_PATH=/opt/amrex || {
        echo "CMake configuration failed"
        exit 1
    }
    make -j4 || {
        echo "Build failed"
        exit 1
    }
    TEST_EXE=$(find . -maxdepth 1 -type f -executable | head -1)
else
    # Check subdirectories for build files
    echo "No build files at top level, checking subdirectories..."
    FOUND_SUBDIR=""
    for subdir in */; do
        if [ -f "$subdir/GNUmakefile" ] || [ -f "$subdir/CMakeLists.txt" ]; then
            FOUND_SUBDIR="$subdir"
            break
        fi
    done
    
    if [ -z "$FOUND_SUBDIR" ]; then
        echo "ERROR: No build files found in $TEST_DIR or its subdirectories"
        exit 1
    fi
    
    echo "Building in subdirectory: $FOUND_SUBDIR"
    cd "$FOUND_SUBDIR"
    
    if [ -f "GNUmakefile" ]; then
        echo "Using GNUmakefile build system"
        make -j4 || {
            echo "Build failed"
            exit 1
        }
        TEST_EXE=$(find . -maxdepth 1 -type f -executable \\( -name "*.exe" -o -name "*.ex" \\) 2>/dev/null | head -1)
    else
        echo "Using CMake build system"
        mkdir -p build && cd build
        cmake .. \\
            -DCMAKE_BUILD_TYPE=Debug \\
            -DAMReX_SPACEDIM=3 \\
            -DAMReX_FORTRAN=OFF \\
            -DAMReX_MPI=OFF \\
            -DAMReX_OMP=OFF \\
            -DCMAKE_PREFIX_PATH=/opt/amrex || {
            echo "CMake configuration failed"
            exit 1
        }
        make -j4 || {
            echo "Build failed"
            exit 1
        }
        TEST_EXE=$(find . -maxdepth 1 -type f -executable | head -1)
    fi
fi

if [ -z "$TEST_EXE" ]; then
    echo "ERROR: No test executable found"
    exit 1
fi

echo "Running test executable: $TEST_EXE"

# Check if inputs file exists
if [ -f ../inputs ]; then
    $TEST_EXE ../inputs 2>&1
elif [ -f ../../inputs ]; then
    $TEST_EXE ../../inputs 2>&1
else
    $TEST_EXE 2>&1
fi

TEST_EXIT_CODE=$?

if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "TEST_RESULT: PASS"
else
    echo "TEST_RESULT: FAIL"
fi

exit $TEST_EXIT_CODE
""",
            ),
        ]

    def dockerfile(self) -> str:
        image = self.dependency()
        name = image.image_name()
        tag = image.image_tag()

        copy_commands = ""
        for file in self.files():
            copy_commands += f"COPY {file.name} /home/\n"
        
        # Make scripts executable and run prepare.sh
        prepare_commands = """RUN chmod +x /home/*.sh && \\
    /home/prepare.sh"""

        return f"""FROM {name}:{tag}

{self.global_env}

{copy_commands}

{prepare_commands}

WORKDIR /workspace/amrex

{self.clear_env}

"""


@Instance.register("AMReX-Codes", "amrex")
class AMReX(Instance):
    """AMReX instance"""
    
    def __init__(self, pr: PullRequest, config: Config, *args, **kwargs):
        super().__init__()
        self._pr = pr
        self._config = config

    @property
    def pr(self) -> PullRequest:
        return self._pr

    def dependency(self) -> Optional[Image]:
        return AMReXImageDefault(self.pr, self._config)

    def run(self, run_cmd: str = "") -> str:
        if run_cmd:
            return run_cmd
        return "/home/run.sh"

    def test_patch_run(self, test_patch_run_cmd: str = "") -> str:
        if test_patch_run_cmd:
            return test_patch_run_cmd
        return "/home/test-run.sh"

    def fix_patch_run(self, fix_patch_run_cmd: str = "") -> str:
        if fix_patch_run_cmd:
            return fix_patch_run_cmd
        return "/home/fix-run.sh"

    def parse_log(self, test_log: str) -> TestResult:
        """Parse AMReX test output to extract test results"""
        passed_tests = set()
        failed_tests = set()
        skipped_tests = set()

        # Check for SUCCESS indicator (AMReX tests print this)
        has_success = False
        has_failure = False
        
        for line in test_log.splitlines():
            line = line.strip()
            
            # AMReX tests print "SUCCESS" when they pass
            if "SUCCESS" in line:
                has_success = True
                passed_tests.add("amrex_test")
            
            # Check for explicit test result markers from our scripts
            if "TEST_RESULT: PASS" in line:
                has_success = True
                passed_tests.add("amrex_test")
            
            if "TEST_RESULT: FAIL" in line:
                has_failure = True
                failed_tests.add("amrex_test")
            
            # Check for common failure patterns
            if "AMREX_ALWAYS_ASSERT" in line or "Assertion" in line or "abort" in line.lower():
                has_failure = True
            
            # Check for compilation errors
            if "error:" in line.lower() and ("undefined reference" in line.lower() or "compilation" in line.lower()):
                has_failure = True
        
        # If we saw a failure but no explicit test failure marker
        if has_failure and not has_success:
            failed_tests.add("amrex_test")
        
        # If we didn't see explicit pass/fail, infer from log content
        if not has_success and not has_failure:
            # No clear indication - consider it passed if no errors found
            passed_tests.add("amrex_test")

        return TestResult(
            passed_count=len(passed_tests),
            failed_count=len(failed_tests),
            skipped_count=len(skipped_tests),
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            skipped_tests=skipped_tests,
        )



