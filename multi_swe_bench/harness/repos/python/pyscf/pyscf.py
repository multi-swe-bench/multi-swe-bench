from typing import Optional

from multi_swe_bench.harness.image import Config, File, Image
from multi_swe_bench.harness.instance import Instance, TestResult
from multi_swe_bench.harness.pull_request import PullRequest


class ImageDefault(Image):
    def __init__(self, pr: PullRequest, config: Config):
        self._pr = pr
        self._config = config
        self._pr_summary = {
            "2895": {"version": "2.9.0", "test_directory": ["pyscf/gto/test"]},
            "2893": {
                "version": "2.9.0",
                "test_directory": ["pyscf/adc/test/test_radc,pyscf/adc/test/test_uadc"],
            },
            "2886": {"version": "2.9.0", "test_directory": ["pyscf/tdscf/test"]},
            "2883": {"version": "2.9.0", "test_directory": ["pyscf/pbc/dft/test"]},
            "2871": {
                "version": "2.9.0",
                "test_directory": ["pyscf/dft/test,pyscf/scf/test"],
            },
            "2870": {"version": "2.9.0", "test_directory": ["pyscf/scf/test"]},
            "2855": {"version": "2.9.0", "test_directory": ["pyscf/geomopt/test"]},
            "2850": {
                "version": "2.9.0",
                "test_directory": [
                    "pyscf/gto/test,pyscf/pbc/df/test,pyscf/pbc/dft/test,pyscf/pbc/gto/test,pyscf/pbc/mp/test,pyscf/pbc/scf/test"
                ],
            },
            "2828": {"version": "2.9.0", "test_directory": ["pyscf/fci/test"]},
            "2826": {"version": "2.9.0", "test_directory": ["pyscf/fci/test"]},
            "2824": {"version": "2.8.0", "test_directory": ["pyscf/geomopt/test"]},
            "2814": {
                "version": "2.9.0",
                "test_directory": [
                    "pyscf/cc/test,pyscf/gto/test,pyscf/mp/test,pyscf/pbc/dft/test"
                ],
            },
            "2803": {"version": "2.9.0", "test_directory": ["pyscf/dft/test"]},
            "2797": {
                "version": "2.9.0",
                "test_directory": ["pyscf/pbc/df/test,pyscf/pbc/dft/test"],
            },
            "2775": {"version": "2.8.0", "test_directory": ["pyscf/fci/test"]},
            "2760": {"version": "2.8.0", "test_directory": ["pyscf/dft/test"]},
            "2733": {"version": "2.8.0", "test_directory": ["pyscf/solvent/test"]},
            "2715": {"version": "2.8.0", "test_directory": ["pyscf/symm/test"]},
            "2709": {"version": "2.8.0", "test_directory": ["pyscf/gto/test"]},
            "2691": {"version": "2.8.0", "test_directory": ["pyscf/solvent/test"]},
            "2677": {
                "version": "2.7.0",
                "test_directory": [
                    "pyscf/mcscf/test,pyscf/pbc/scf/test,pyscf/pbc/tools/test,pyscf/tools/test"
                ],
            },
            "2676": {"version": "2.8.0", "test_directory": ["pyscf/df/test"]},
            "2611": {"version": "2.8.0", "test_directory": ["pyscf/x2c/test"]},
            "2577": {"version": "2.7.0", "test_directory": ["pyscf/pbc/df/test"]},
            "2574": {"version": "2.7.0", "test_directory": ["pyscf/dft/test"]},
            "2531": {"version": "2.7.0", "test_directory": ["pyscf/cc/test"]},
            "2530": {"version": "2.7.0", "test_directory": ["pyscf/soscf/test"]},
            "2528": {
                "version": "2.7.0",
                "test_directory": ["pyscf/pbc/tdscf/test,pyscf/tdscf/test"],
            },
            "2526": {
                "version": "2.7.0",
                "test_directory": ["pyscf/gto/test,pyscf/soscf/test,pyscf/tdscf/test"],
            },
            "2525": {
                "version": "2.7.0",
                "test_directory": [
                    "pyscf/dft/test,pyscf/grad/test,pyscf/hessian/test,pyscf/pbc/df/test,pyscf/pbc/dft/test,pyscf/pbc/scf/test,pyscf/pbc/tdscf/test,pyscf/tdscf/test"
                ],
            },
            "2524": {"version": "2.7.0", "test_directory": ["pyscf/cc/test"]},
            "2499": {"version": "2.7.0", "test_directory": ["pyscf/dft/test"]},
            "2496": {"version": "2.7.0", "test_directory": ["pyscf/mcscf/test"]},
            "2457": {"version": "2.7.0", "test_directory": ["pyscf/df/test"]},
            "2396": {"version": "2.6.2", "test_directory": ["pyscf/x2c/test"]},
            "2395": {"version": "2.6.2", "test_directory": ["pyscf/fci/test"]},
            "2387": {
                "version": "2.6.2",
                "test_directory": [
                    ".github/workflows,pyscf/pbc/gto/test,pyscf/pbc/scf/test,pyscf/pbc/tools/test,pyscf/scf/test"
                ],
            },
            "2382": {
                "version": "2.6.2",
                "test_directory": [
                    "pyscf/adc/test/test_radc,pyscf/grad/test,pyscf/pbc/tdscf/test,pyscf/tdscf/test,pyscf/x2c/test"
                ],
            },
            "2380": {"version": "2.6.2", "test_directory": ["pyscf/gto/test"]},
            "2373": {"version": "2.6.2", "test_directory": ["pyscf/tdscf/test"]},
            "2371": {"version": "2.6.2", "test_directory": ["pyscf/sgx/test"]},
            "2366": {"version": "2.6.2", "test_directory": ["pyscf/dft/test"]},
            "2364": {"version": "2.6.2", "test_directory": ["pyscf/dft/test"]},
            "2360": {"version": "2.6.2", "test_directory": ["pyscf/pbc/gto/test"]},
            "2359": {"version": "2.6.2", "test_directory": ["pyscf/pbc/tdscf/test"]},
            "2357": {"version": "2.6.2", "test_directory": ["pyscf/fci/test"]},
            "2356": {"version": "2.6.2", "test_directory": ["pyscf/scf/test"]},
            "2354": {"version": "2.6.2", "test_directory": ["pyscf/gto/test"]},
            "2353": {
                "version": "2.6.2",
                "test_directory": ["pyscf/adc/test/test_radc"],
            },
            "2349": {"version": "2.6.2", "test_directory": ["pyscf/mcscf/test"]},
            "2320": {"version": "2.6.2", "test_directory": [".github/workflows"]},
            "2307": {"version": "2.6.2", "test_directory": ["pyscf/fci/test"]},
            "2306": {"version": "2.6.2", "test_directory": ["pyscf/fci/test"]},
            "2305": {"version": "2.6.2", "test_directory": ["pyscf/fci/test"]},
            "2299": {"version": "2.6.2", "test_directory": ["pyscf/scf/test"]},
            "2290": {"version": "2.6.2", "test_directory": ["pyscf/scf/test"]},
            "2279": {"version": "2.6.2", "test_directory": ["pyscf/tdscf/test"]},
            "2262": {"version": "2.6.0", "test_directory": ["pyscf/pbc/dft/test"]},
            "2240": {"version": "2.5.0", "test_directory": ["pyscf/df/test"]},
            "2188": {"version": "2.5.0", "test_directory": ["pyscf/dft/test"]},
            "2186": {
                "version": "2.6.2",
                "test_directory": [
                    "pyscf/df/test,pyscf/dft/test,pyscf/grad/test,pyscf/hessian/test,pyscf/lib/test,pyscf/pbc/dft/test,pyscf/scf/test,pyscf/sgx/test,pyscf/solvent/test,pyscf/soscf/test,pyscf/tdscf/test,pyscf/x2c/test"
                ],
            },
            "2173": {"version": "2.5.0", "test_directory": ["pyscf/solvent/test"]},
            "2172": {"version": "2.5.0", "test_directory": ["pyscf/pbc/dft/test"]},
            "2164": {"version": "2.5.0", "test_directory": ["pyscf/pbc/tools/test"]},
            "2163": {"version": "2.5.0", "test_directory": ["pyscf/pbc/df/test"]},
            "2144": {"version": "2.5.0", "test_directory": [".,.github/workflows"]},
            "2084": {"version": "2.5.0", "test_directory": ["pyscf/dft/test"]},
            "2078": {
                "version": "2.5.0",
                "test_directory": [
                    "pyscf/lib/test,pyscf/pbc/dft/test,pyscf/pbc/gto/pseudo/test,pyscf/pbc/gto/test,pyscf/pbc/scf/test"
                ],
            },
            "2063": {"version": "2.4.0", "test_directory": ["pyscf/df/test"]},
            "2062": {"version": "2.4.0", "test_directory": ["pyscf/fci/test"]},
            "2061": {
                "version": "2.4.0",
                "test_directory": ["pyscf/dft/test,pyscf/scf/test"],
            },
            "2059": {"version": "2.4.0", "test_directory": ["pyscf/cc/test"]},
            "2050": {"version": "2.4.0", "test_directory": ["pyscf/fci/test"]},
            "2049": {"version": "2.4.0", "test_directory": ["pyscf/pbc/gto/test"]},
            "2045": {"version": "2.4.0", "test_directory": ["pyscf/gto/test"]},
            "2041": {"version": "2.4.0", "test_directory": ["pyscf/pbc/tools/test"]},
            "2023": {"version": "2.4.0", "test_directory": ["pyscf/mcscf/test"]},
            "2010": {"version": "2.4.0", "test_directory": ["pyscf/dft/test"]},
            "2001": {"version": "2.4.0", "test_directory": ["pyscf/grad/test"]},
            "1991": {"version": "2.4.0", "test_directory": ["pyscf/mp/test"]},
            "1990": {"version": "2.4.0", "test_directory": ["pyscf/lo/test"]},
            "1963": {"version": "2.4.0", "test_directory": ["pyscf/tools/test"]},
            "1960": {"version": "2.4.0", "test_directory": ["pyscf/pbc/dft/test"]},
            "1947": {"version": "2.4.0", "test_directory": ["pyscf/pbc/df/test"]},
            "1943": {"version": "2.4.0", "test_directory": ["pyscf/gto/test"]},
            "1927": {"version": "2.4.0", "test_directory": ["pyscf/pbc/dft/test"]},
            "1923": {
                "version": "2.4.0",
                "test_directory": ["pyscf/pbc/adc/test,pyscf/pbc/df/test"],
            },
            "1914": {"version": "2.4.0", "test_directory": ["pyscf/grad/test"]},
            "1900": {"version": "2.3.0", "test_directory": [".github/workflows"]},
            "1897": {
                "version": "2.3.0",
                "test_directory": [
                    "pyscf/grad/test,pyscf/pbc/dft/test,pyscf/pbc/tdscf/test,pyscf/tdscf/test"
                ],
            },
            "1891": {"version": "2.3.0", "test_directory": ["pyscf/gto/test"]},
            "1869": {"version": "2.3.0", "test_directory": ["pyscf/mcscf/test"]},
            "1859": {
                "version": "2.3.0",
                "test_directory": [
                    "pyscf/cc/test,pyscf/ci/test,pyscf/df/test,pyscf/dft/test,pyscf/fci/test,pyscf/grad/test,pyscf/gto/test,pyscf/mcscf/test,pyscf/mp/test,pyscf/pbc/cc/test,pyscf/pbc/ci/test,pyscf/pbc/df/test,pyscf/pbc/dft/test,pyscf/pbc/gto/test,pyscf/pbc/gw/test,pyscf/pbc/scf/test,pyscf/qmmm/test,pyscf/scf/test,pyscf/sgx/test,pyscf/solvent/test,pyscf/soscf/test,pyscf/tdscf/test,pyscf/tools/test,pyscf/x2c/test"
                ],
            },
            "1845": {"version": "2.3.0", "test_directory": ["pyscf/fci/test"]},
            "1841": {"version": "2.6.2", "test_directory": ["pyscf/scf/test"]},
            "1834": {
                "version": "2.3.0",
                "test_directory": [
                    "pyscf/lib/gto/test,pyscf/lib/test,pyscf/mcscf/test,pyscf/pbc/symm/test"
                ],
            },
            "1824": {
                "version": "2.2.1",
                "test_directory": ["pyscf/adc/test/test_radc,pyscf/adc/test/test_uadc"],
            },
            "1821": {"version": "2.3.0", "test_directory": ["pyscf/pbc/gto/test"]},
            "1813": {"version": "2.3.0", "test_directory": ["pyscf/fci/test"]},
            "1803": {"version": "2.3.0", "test_directory": ["pyscf/lo/test"]},
            "1788": {"version": "2.3.0", "test_directory": ["pyscf/dft/test"]},
            "1773": {
                "version": "2.3.0",
                "test_directory": [
                    "pyscf/pbc/mp/test,pyscf/pbc/symm/test,pyscf/pbc/tools/test"
                ],
            },
            "1734": {"version": "2.2.1", "test_directory": ["pyscf/mcscf/test"]},
            "1723": {"version": "2.2.1", "test_directory": ["pyscf/gto/test"]},
            "1700": {
                "version": "2.2.1",
                "test_directory": ["pyscf/geomopt/test,pyscf/grad/test"],
            },
            "1681": {"version": "2.2.0", "test_directory": ["pyscf/dft/test"]},
            "1677": {"version": "2.2.0", "test_directory": ["pyscf/qmmm/test"]},
            "1675": {"version": "2.2.0", "test_directory": ["pyscf/fci/test"]},
            "1672": {"version": "2.2.0", "test_directory": ["pyscf/fci/test"]},
            "1664": {"version": "2.2.0", "test_directory": ["pyscf/df/test"]},
            "1654": {
                "version": "2.2.0",
                "test_directory": ["pyscf/ci/test,pyscf/lib/test,pyscf/mcscf/test"],
            },
            "1647": {"version": "2.2.0", "test_directory": ["pyscf/pbc/dft/test"]},
            "1643": {"version": "2.2.0", "test_directory": ["pyscf/symm/test"]},
            "1638": {"version": "2.2.0", "test_directory": ["pyscf/scf/test"]},
            "1623": {
                "version": "2.2.1",
                "test_directory": ["pyscf/fci/test,pyscf/mcscf/test"],
            },
            "1622": {
                "version": "2.2.1",
                "test_directory": [
                    "pyscf/cc/test,pyscf/fci/test,pyscf/lib/test,pyscf/mp/test,pyscf/pbc/cc/test,pyscf/pbc/ci/test,pyscf/pbc/df/test,pyscf/pbc/dft/test,pyscf/pbc/gto/pseudo/test,pyscf/pbc/gto/test,pyscf/pbc/lib/test,pyscf/pbc/mp/test,pyscf/pbc/scf/test,pyscf/pbc/tools/test"
                ],
            },
            "1620": {"version": "2.1.1", "test_directory": ["pyscf/gto/test"]},
            "1594": {"version": "2.1.1", "test_directory": ["pyscf/pbc/dft/test"]},
            "1584": {"version": "2.1.1", "test_directory": ["pyscf/pbc/lib/test"]},
            "1578": {
                "version": "2.1.1",
                "test_directory": [
                    "pyscf/pbc/cc/test,pyscf/pbc/dft/test,pyscf/pbc/lib/test,pyscf/pbc/mp/test,pyscf/pbc/scf/test,pyscf/pbc/symm/test,pyscf/pbc/tools/test"
                ],
            },
            "1532": {"version": "2.2.0", "test_directory": ["pyscf/tools/test"]},
            "1529": {
                "version": "2.1.1",
                "test_directory": [
                    "pyscf/fci/test,pyscf/gto/test,pyscf/mcscf/test,pyscf/soscf/test"
                ],
            },
            "1486": {"version": "2.1.1", "test_directory": ["pyscf/grad/test"]},
            "1481": {
                "version": "2.2.0",
                "test_directory": [
                    "pyscf/dft/test,pyscf/eph/test,pyscf/grad/test,pyscf/hessian/test,pyscf/pbc/grad/test,pyscf/pbc/scf/test,pyscf/scf/test,pyscf/soscf/test,pyscf/tdscf/test,pyscf/x2c/test"
                ],
            },
            "1450": {"version": "2.1.1", "test_directory": ["pyscf/ci/test"]},
            "1442": {"version": "2.1.0", "test_directory": ["pyscf/mcscf/test"]},
            "1441": {
                "version": "2.1.1",
                "test_directory": [
                    "pyscf/lib/test,pyscf/pbc/cc/test,pyscf/pbc/df/test,pyscf/pbc/dft/test,pyscf/pbc/gto/test,pyscf/pbc/mp/test,pyscf/pbc/scf/test,pyscf/pbc/tools,pyscf/pbc/tools/test"
                ],
            },
            "1432": {
                "version": "2.1.1",
                "test_directory": ["pyscf/df/test,pyscf/grad/test"],
            },
            "1429": {
                "version": "2.1.0",
                "test_directory": ["pyscf/pbc/mp/test,pyscf/pbc/x2c/test"],
            },
            "1426": {"version": "2.1.0", "test_directory": ["pyscf/cc/test"]},
            "1417": {"version": "2.1.0", "test_directory": ["pyscf/grad/test"]},
            "1416": {"version": "2.2.0", "test_directory": ["pyscf/scf/test"]},
            "1411": {"version": "2.1.1", "test_directory": ["pyscf/ao2mo/test"]},
            "1402": {
                "version": "2.1.0",
                "test_directory": [
                    "pyscf/gto/test,pyscf/mp/test,pyscf/pbc/adc/test,pyscf/pbc/cc/test,pyscf/pbc/df/test"
                ],
            },
        }

    @property
    def pr(self) -> PullRequest:
        return self._pr

    @property
    def config(self) -> Config:
        return self._config

    def dependency(self) -> str:
        return "python:3.7-slim"

    def image_prefix(self) -> str:
        return "envagent"

    def image_tag(self) -> str:
        return f"pr-{self.pr.number}"

    def workdir(self) -> str:
        return f"pr-{self.pr.number}"

    def files(self) -> list[File]:
        # Get test directories from PR object, default to a common pyscf test pattern if not available

        test_dirs = self._pr_summary.get(str(self.pr.number), {}).get(
            "test_directory", []
        )
        test_dir_cmd = " ".join(test_dirs)
        if not test_dirs:
            raise ValueError(f"No test directories found for PR #{self.pr.number}")

        print(f"Test directories for PR #{self.pr.number}: {test_dirs}")

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
                """#!/bin/bash
cd /home/{pr.repo}
python -m pytest {test_dir} --no-header -rA --tb=no -p no:cacheprovider
""".format(pr=self.pr, test_dir=test_dir_cmd),
            ),
            File(
                ".",
                "test-run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
if ! git -C /home/{pr.repo} apply --whitespace=nowarn /home/test.patch; then
    echo "Error: git apply failed" >&2
    exit 1  
fi
python -m pytest {test_dir} --no-header -rA --tb=no -p no:cacheprovider
""".format(pr=self.pr, test_dir=test_dir_cmd),
            ),
            File(
                ".",
                "fix-run.sh",
                """#!/bin/bash
cd /home/{pr.repo}
if ! git -C /home/{pr.repo} apply --whitespace=nowarn  /home/test.patch /home/fix.patch; then
    echo "Error: git apply failed" >&2
    exit 1  
fi
python -m pytest {test_dir} --no-header -rA --tb=no -p no:cacheprovider

""".format(pr=self.pr, test_dir=test_dir_cmd),
            ),
        ]

    def dockerfile(self) -> str:
        copy_commands = ""
        for file in self.files():
            copy_commands += f"COPY {file.name} /home/\n"

        # Get PySCF version from PR summary
        pyscf_version = self._pr_summary.get(str(self.pr.number), {}).get(
            "version", None
        )
        if not pyscf_version:
            raise ValueError(f"No PySCF version found for PR #{self.pr.number}")


        print(self.pr.base.sha)

        dockerfile_content = f"""
        FROM titouandu/pyscf-build:{pyscf_version}

        WORKDIR /home/pyscf

        RUN git fetch origin && \
            git fetch --no-tags origin "pull/{self.pr.number}/head:pr-{self.pr.number}" && \
            git checkout {self.pr.base.sha}

        """

        dockerfile_content += f"""{copy_commands}"""

        return dockerfile_content.format(pr=self.pr)


@Instance.register("pyscf", "pyscf")
class PYSCF(Instance):
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

        return "bash /home/run.sh"

    def test_patch_run(self, test_patch_run_cmd: str = "") -> str:
        if test_patch_run_cmd:
            return test_patch_run_cmd

        return "bash /home/test-run.sh"

    def fix_patch_run(self, fix_patch_run_cmd: str = "") -> str:
        if fix_patch_run_cmd:
            return fix_patch_run_cmd

        return "bash /home/fix-run.sh"

    def parse_log(self, log: str) -> TestResult:
        # Parse the log content and extract test execution results.
        passed_tests = set()
        failed_tests = set()
        skipped_tests = set()
        import re
        import json

        for line in log.splitlines():
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
            "skipped_tests": skipped_tests,
        }

        return TestResult(
            passed_count=len(passed_tests),
            failed_count=len(failed_tests),
            skipped_count=len(skipped_tests),
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            skipped_tests=skipped_tests,
        )
