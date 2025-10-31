import re
from typing import Optional

from multi_swe_bench.harness.image import Config, File, Image
from multi_swe_bench.harness.instance import Instance, TestResult
from multi_swe_bench.harness.pull_request import PullRequest


OPENMM_TEST_DIRECTORY = {
    3313: ["wrappers/python/tests/TestForceField.py"],
    3324: ["wrappers/python/tests/TestCharmmFiles.py"],
    3416: ["wrappers/python/tests/TestAmberPrmtopFile.py"],
    3480: ["wrappers/python/tests/TestModeller.py"],
    3493: ["wrappers/python/tests/TestForceField.py"],
    3506: ["wrappers/python/tests/TestAmberPrmtopFile.py"],
    3508: ["wrappers/python/tests/TestAPIUnits.py"],
    3512: ["plugins/drude/tests/TestDrudeLangevinIntegrator.h", "plugins/drude/tests/TestDrudeNoseHoover.h"],
    3522: ["wrappers/python/tests/TestPdbFile.py"],
    3537: ["wrappers/python/tests/TestModeller.py"],
    3565: ["wrappers/python/tests/TestAPIUnits.py"],
    3575: ["tests/TestNonbondedForce.h"],
    3614: ["wrappers/python/tests/TestSimulatedTempering.py"],
    3667: ["platforms/cuda/tests/TestCudaFFT3D.cpp", "platforms/opencl/tests/TestOpenCLFFT.cpp"],
    3711: ["tests/TestCustomCVForce.h"],
    3760: ["wrappers/python/tests/TestModeller.py"],
    3769: ["tests/TestCustomBondForce.h"],
    3791: ["wrappers/python/tests/TestIntegrators.py"],
    3819: ["wrappers/python/tests/TestForceField.py"],
    3886: ["tests/TestLocalEnergyMinimizer.h"],
    3931: ["wrappers/python/tests/TestPdbReporter.py"],
    4070: ["tests/TestNonbondedForce.h"],
    4094: ["wrappers/python/tests/TestAmberPrmtopFile.py"],
    4128: ["plugins/drude/tests/TestDrudeNoseHoover.h"],
    4168: ["wrappers/python/tests/TestXtcFile.py"],
    4191: ["tests/TestCustomIntegrator.h"],
    4206: ["tests/TestCustomIntegrator.h"],
    4219: ["wrappers/python/tests/TestAmberPrmtopFile.py", "wrappers/python/tests/TestForceField.py"],
    4231: ["platforms/cpu/tests/TestCpuCustomCPPForce.cpp", "platforms/cuda/tests/TestCudaCustomCPPForce.cpp", "platforms/opencl/tests/TestOpenCLCustomCPPForce.cpp", "platforms/reference/tests/TestReferenceCustomCPPForce.cpp", "tests/TestCustomCPPForce.h"],
    4317: ["serialization/tests/TestSerializeATMForce.cpp"],
    4319: ["wrappers/python/tests/TestAPIUnits.py"],
    4323: ["wrappers/python/tests/TestModeller.py"],
    4356: ["plugins/drude/tests/TestDrudeSCFIntegrator.h"],
    4451: ["tests/TestCustomHbondForce.h"],
    4495: ["tests/TestATMForce.h"],
    4523: ["plugins/drude/tests/TestDrudeForce.h"],
    4528: ["wrappers/python/tests/TestModeller.py"],
    4585: ["wrappers/python/tests/TestModeller.py"],
    4602: ["wrappers/python/tests/TestAmberInpcrdFile.py"],
    4630: ["wrappers/python/tests/TestPdbFile.py"],
    4641: ["serialization/tests/TestSerializeIntegrator.cpp"],
    4645: ["platforms/cuda/tests/TestCudaCustomCPPForce.cpp", "platforms/hip/tests/TestHipCustomCPPForce.cpp", "platforms/opencl/tests/TestOpenCLCustomCPPForce.cpp"],
    4647: ["plugins/amoeba/serialization/tests/TestSerializeAmoebaGeneralizedKirkwoodForce.cpp", "plugins/amoeba/serialization/tests/TestSerializeAmoebaVdwForce.cpp", "plugins/amoeba/tests/TestAmoebaGeneralizedKirkwoodForce.h", "plugins/amoeba/tests/TestAmoebaVdwForce.h", "plugins/amoeba/tests/TestWcaDispersionForce.h", "wrappers/python/tests/TestAPIUnits.py"],
    4671: ["wrappers/python/tests/TestSimulation.py"],
    4694: ["devtools/ci/gh-actions/conda-envs/build-ubuntu-latest-hip.yml", "devtools/ci/gh-actions/conda-envs/build-ubuntu-latest.yml", "devtools/ci/gh-actions/conda-envs/build-windows-latest.yml"],
    4732: ["tests/TestNonbondedForce.h"],
    4734: ["plugins/drude/serialization/tests/TestSerializeDrudeLangevinIntegrator.cpp", "plugins/drude/serialization/tests/TestSerializeDrudeNoseHooverIntegrator.cpp", "serialization/tests/TestSerializeIntegrator.cpp", "serialization/tests/TestSerializeNoseHooverIntegrator.cpp"],
    4741: ["wrappers/python/tests/TestDcdFile.py", "wrappers/python/tests/TestXtcFile.py"],
    4767: ["wrappers/python/tests/TestUnits.py"],
    4770: ["wrappers/python/tests/TestForceField.py"],
    4794: ["wrappers/python/tests/TestXtcFile.py"],
    4795: ["wrappers/python/tests/TestForceField.py"],
    4830: ["wrappers/python/tests/TestCharmmFiles.py"],
    4832: ["wrappers/python/tests/TestAmberPrmtopFile.py"],
    4834: ["tests/TestATMForce.h"],
    4851: ["tests/TestATMForce.h"],
    4852: ["wrappers/python/tests/TestForceField.py"],
    4875: ["wrappers/python/tests/TestDcdFile.py", "wrappers/python/tests/TestXtcFile.py"],
    4879: ["wrappers/python/tests/TestDcdFile.py", "wrappers/python/tests/TestXtcFile.py"],
    4898: ["wrappers/python/tests/TestModeller.py"],
    4907: ["tests/TestEwald.h"],
    4920: ["plugins/amoeba/tests/TestAmoebaMultipoleForce.h", "plugins/amoeba/tests/TestHippoNonbondedForce.h"],
    4956: ["wrappers/python/tests/TestForceField.py"],
    4980: ["tests/TestMonteCarloBarostat.h"],
    4989: ["wrappers/python/tests/TestForceField.py"],
    4995: ["platforms/cuda/tests/TestCudaQTBIntegrator.cpp", "platforms/hip/tests/TestHipQTBIntegrator.cpp", "platforms/opencl/tests/TestOpenCLQTBIntegrator.cpp", "platforms/reference/tests/TestReferenceQTBIntegrator.cpp", "serialization/tests/TestSerializeQTBIntegrator.cpp", "tests/TestQTBIntegrator.h", "wrappers/python/tests/TestAPIUnits.py"],
    5031: ["platforms/cuda/tests/TestCudaRGForce.cpp", "platforms/hip/tests/TestHipRGForce.cpp", "platforms/opencl/tests/TestOpenCLRGForce.cpp", "platforms/reference/tests/TestReferenceRGForce.cpp", "serialization/tests/TestSerializeRGForce.cpp", "tests/TestRGForce.h"],
    5044: ["wrappers/python/tests/TestAmberPrmtopFile.py", "wrappers/python/tests/TestCharmmFiles.py", "wrappers/python/tests/TestDesmondDMSFile.py", "wrappers/python/tests/TestForceField.py", "wrappers/python/tests/TestGromacsTopFile.py"],
    5065: ["wrappers/python/tests/TestForceField.py"],
    5066: ["wrappers/python/tests/TestModeller.py"],
    5091: ["wrappers/python/tests/TestForceField.py"],
    5109: ["platforms/cuda/tests/TestCudaConstantPotentialForce.cpp", "platforms/hip/tests/TestHipConstantPotentialForce.cpp", "platforms/opencl/tests/TestOpenCLConstantPotentialForce.cpp", "tests/TestConstantPotentialForce.h"],
    5114: ["tests/TestMonteCarloBarostat.h", "wrappers/python/tests/TestAPIUnits.py"],
}


class ImageDefault(Image):
    def __init__(self, pr: PullRequest, config: Config):
        self._pr = pr
        self._config = config

    @property
    def pr(self) -> PullRequest:
        return self._pr

    @property
    def config(self) -> Config:
        return self._config

    def dependency(self) -> str:
        return "openmm:built"
    
    def image_prefix(self) -> str:
        return "envagent"
       
    def image_tag(self) -> str:
        return f"pr-{self.pr.number}"

    def workdir(self) -> str:
        return f"pr-{self.pr.number}"

    def _get_python_test_cmd(self) -> str:
        """Generate bash command for Python tests"""
        if not self._python_tests:
            return ""
        
        # Build individual pytest commands for each test file with its directory
        # This handles tests in different directories correctly
        commands = []
        for test_path in self._python_tests:
            test_dir = '/'.join(test_path.split('/')[:-1])
            test_file = test_path.split('/')[-1]
            dir_path = f'/home/openmm/{test_dir}'
            
            commands.append(f"""    (cd {dir_path} && python -m pytest {test_file} --no-header -rA --tb=no -p no:cacheprovider)""")
        
        if commands:
            return '\n'.join(commands)
        return ""

    def _get_cpp_test_cmd(self) -> str:
        """Generate bash command for C++ tests"""
        if not self._cpp_tests:
            return ""
        # Extract test names (e.g., tests/TestNonbondedForce.h -> TestNonbondedForce)
        # This runs in Python during harness setup, not in Docker
        test_names = []
        for test_file in self._cpp_tests:
            # Get basename and remove extension
            basename = test_file.split('/')[-1]  # Get last part of path
            test_name = basename.rsplit('.', 1)[0]  # Remove extension
            test_names.append(test_name)
        test_pattern = '|'.join(test_names)
        return f"""if [ -n "{test_pattern}" ]; then
    # Find and run ctest from the build directory
    if [ -d "/home/openmm/build" ]; then
        cd /home/openmm/build
        ctest -R "{test_pattern}"
    elif [ -d "/home/openmm" ]; then
        cd /home/openmm
        ctest -R "{test_pattern}"
    fi
fi"""

    def files(self) -> list[File]:
        test_dirs_list = OPENMM_TEST_DIRECTORY.get(self.pr.number, None)
        
        if test_dirs_list is None:
            self._python_tests = []
            self._cpp_tests = []
        else:
            python_tests = [t for t in test_dirs_list if t.endswith('.py')]
            cpp_tests = [t for t in test_dirs_list if t.endswith('.h') or t.endswith('.cpp')]
            
            self._python_tests = python_tests
            self._cpp_tests = cpp_tests
        
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
                    "run.sh",
                    f"""#!/bin/bash
cd /home/openmm

# Test OpenMM installation
/home/scripts/test_openmm.sh

# Run Python tests if any
{self._get_python_test_cmd()}

# Run C++ tests if any
{self._get_cpp_test_cmd()}
""",
                ),
                File(
                    ".",
                    "test-run.sh",
                    f"""#!/bin/bash
cd /home/openmm
if ! git apply --whitespace=nowarn /home/test.patch; then
    echo "Error: git apply failed" >&2
    exit 1  
fi
# Recompile after applying patch
/home/scripts/build_fast.sh -i || /home/scripts/build.sh || /home/scripts/build_no_c_wrappers.sh

# Test OpenMM installation
/home/scripts/test_openmm.sh

# Run Python tests if any
{self._get_python_test_cmd()}

# Run C++ tests if any
{self._get_cpp_test_cmd()}
""",
                ),
                File(
                    ".",
                    "fix-run.sh",
                    f"""#!/bin/bash
cd /home/openmm
if ! git apply --whitespace=nowarn /home/test.patch /home/fix.patch; then
    echo "Error: git apply failed" >&2
    exit 1  
fi
# Recompile after applying patches
/home/scripts/build_fast.sh -i || /home/scripts/build.sh || /home/scripts/build_no_c_wrappers.sh

# Test OpenMM installation
/home/scripts/test_openmm.sh

# Run Python tests if any
{self._get_python_test_cmd()}

# Run C++ tests if any
{self._get_cpp_test_cmd()}
""",
                ),
        ]

    def dockerfile(self) -> str:
        # Skip build if PR number is not in the dictionary
        if self.pr.number not in OPENMM_TEST_DIRECTORY:
            # Return a minimal valid dockerfile that won't cause errors
            return """FROM titouandu/openmm:python310
WORKDIR /home

# No files to copy - test data not available
RUN echo "Skipping build for PR %s - not in OPENMM_TEST_DIRECTORY" > /dev/null
""" % self.pr.number
        
        copy_commands = ""
        for file in self.files():
            copy_commands += f"COPY {file.name} /home/\n"

        # print(f"Base SHA: {self.pr.base.sha}")
        
        dockerfile_content = f"""
FROM titouandu/openmm:python310

WORKDIR /home

# Copy test files
{copy_commands}

# Make scripts executable
RUN chmod +x /home/*.sh

# Switch to the specific commit from the PR (OpenMM is already built)
RUN /home/scripts/setup_versions.sh setup {self.pr.base.sha}

# Verify OpenMM is still working after checkout
RUN /home/scripts/test_openmm.sh

# Set up environment for Python 3.10
ENV OPENMM_DIR=/usr/local/openmm
ENV LD_LIBRARY_PATH=$OPENMM_DIR/lib:$LD_LIBRARY_PATH
ENV PYTHONPATH=$OPENMM_DIR/lib/python3.10/site-packages:$PYTHONPATH
ENV PATH=$OPENMM_DIR/bin:$PATH
"""
        
        return dockerfile_content


@Instance.register("openmm", "openmm")
class OpenMM(Instance):
    def __init__(self, pr: PullRequest, config: Config, *args, **kwargs):
        super().__init__()
        self._pr = pr
        self._config = config

    @property
    def pr(self) -> PullRequest:
        return self._pr

    def dependency(self) -> Optional[Image]:
        return ImageDefault(self.pr, self._config)

    def run(self, run_cmd: str = "") -> str:
        if run_cmd:
            return run_cmd

        return 'bash /home/run.sh'

    def test_patch_run(self, test_patch_run_cmd: str = "") -> str:
        if test_patch_run_cmd:
            return test_patch_run_cmd

        return "bash /home/test-run.sh"

    def fix_patch_run(self, fix_patch_run_cmd: str = "") -> str:
        if fix_patch_run_cmd:
            return fix_patch_run_cmd

        return "bash /home/fix-run.sh"

    def parse_log(self, log: str) -> TestResult:
        passed_tests = set() 
        failed_tests = set() 
        skipped_tests = set() 
        
        for line in log.splitlines():
            if 'Test' in line and '#' in line and ('Passed' in line or '***Failed' in line):
                match = re.search(r'Test\s+#(\d+):\s+(\S+)', line)
                if match:
                    test_num = match.group(1)
                    test_name = match.group(2)
                    
                    if '***Failed' in line:
                        failed_tests.add(test_name)
                    elif 'Passed' in line:
                        passed_tests.add(test_name)
            
            if 'tests passed' in line and 'tests failed' in line:
                pass_match = re.search(r'(\d+)% tests passed', line)
                fail_match = re.search(r'(\d+) tests failed', line)
            
            if re.match(r'\s*\d+\s+-\s+(\S+)', line) and '(Failed)' in line:
                match = re.match(r'\s*\d+\s+-\s+(\S+)', line)
                if match:
                    failed_tests.add(match.group(1))
            
            if line.startswith("PASSED"):
                match = re.match(r"PASSED\s+(.*)", line)
                if match:
                    passed_tests.add(match.group(1).strip())
            elif line.startswith("FAILED"):
                match = re.match(r"FAILED\s+([^\s-]+)", line)
                if match:
                    failed_tests.add(match.group(1).strip())
        
        parsed_results = {
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "skipped_tests": skipped_tests
        }
        

        return TestResult(
            passed_count=len(passed_tests),
            failed_count=len(failed_tests),
            skipped_count=len(skipped_tests),
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            skipped_tests=skipped_tests,
        )
