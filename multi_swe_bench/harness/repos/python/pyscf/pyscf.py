from typing import Optional

from multi_swe_bench.harness.image import Config, File, Image
from multi_swe_bench.harness.instance import Instance, TestResult
from multi_swe_bench.harness.pull_request import PullRequest

# Set to True to test individual files, False to test directories only
TEST_INDIVIDUAL_FILES = False


class ImageDefault(Image):
    def __init__(self, pr: PullRequest, config: Config):
        self._pr = pr
        self._config = config
        self._pr_summary = {
            "2886": {
                "version": "2.9.0",
                "test_directory": [
                    "pyscf/tdscf/test/test_tdgks.py",
                    "pyscf/tdscf/test/test_tdrhf.py",
                    "pyscf/tdscf/test/test_tduhf.py",
                ],
            },
            "2871": {
                "version": "2.9.0",
                "test_directory": [
                    "pyscf/dft/test/test_gks.py",
                    "pyscf/dft/test/test_h2o.py",
                    "pyscf/scf/test/test_response_function.py",
                ],
            },
            "2870": {
                "version": "2.9.0",
                "test_directory": ["pyscf/scf/test/test_dhf.py"],
            },
            "2826": {
                "version": "2.9.0",
                "test_directory": ["pyscf/fci/test/test_rdm.py"],
            },
            "2803": {
                "version": "2.9.0",
                "test_directory": ["pyscf/dft/test/test_h2o.py"],
            },
            "2797": {
                "version": "2.9.0",
                "test_directory": [
                    "pyscf/pbc/df/test/test_df.py",
                    "pyscf/pbc/dft/test/test_uks.py",
                ],
            },
            "2715": {
                "version": "2.8.0",
                "test_directory": [
                    "pyscf/symm/test/test_basis.py",
                    "pyscf/symm/test/test_geom.py",
                ],
            },
            "2691": {
                "version": "2.8.0",
                "test_directory": [
                    "pyscf/solvent/test/test_pcm_grad.py",
                    "pyscf/solvent/test/test_pcm_hessian.py",
                ],
            },
            "2676": {
                "version": "2.8.0",
                "test_directory": ["pyscf/df/test/test_df_jk.py"],
            },
            "2611": {
                "version": "2.8.0",
                "test_directory": ["pyscf/x2c/test/test_x2c.py"],
            },
            "2577": {
                "version": "2.8.0",
                "test_directory": ["pyscf/pbc/df/test/test_aft.py"],
            },
            "2574": {
                "version": "2.8.0",
                "test_directory": ["pyscf/dft/test/test_libxc.py"],
            },
            "2531": {
                "version": "2.8.0",
                "test_directory": ["pyscf/cc/test/test_gccsd.py"],
            },
            "2524": {
                "version": "2.8.0",
                "test_directory": ["pyscf/cc/test/test_uccsd.py"],
            },
            "2499": {
                "version": "2.8.0",
                "test_directory": ["pyscf/dft/test/test_grids.py"],
            },
            "2457": {
                "version": "2.8.0",
                "test_directory": ["pyscf/df/test/test_df.py"],
            },
            "2396": {
                "version": "2.6.2",
                "test_directory": ["pyscf/x2c/test/test_x2c.py"],
            },
            "2373": {
                "version": "2.6.2",
                "test_directory": ["pyscf/tdscf/test/test_tdrhf.py"],
            },
            "2371": {
                "version": "2.6.2",
                "test_directory": ["pyscf/sgx/test/test_sgx.py"],
            },
            "2364": {
                "version": "2.6.2",
                "test_directory": ["pyscf/dft/test/test_libxc.py"],
            },
            "2357": {
                "version": "2.6.2",
                "test_directory": ["pyscf/fci/test/test_rdm.py"],
            },
            "2356": {
                "version": "2.6.2",
                "test_directory": ["pyscf/scf/test/test_addons.py"],
            },
            "2354": {
                "version": "2.6.2",
                "test_directory": ["pyscf/gto/test/test_mole.py"],
            },
            "2353": {
                "version": "2.6.2",
                "test_directory": [
                    "pyscf/adc/test/test_radc/test_H2O_radc_ea.py",
                    "pyscf/adc/test/test_radc/test_H2O_radc_ip.py",
                    "pyscf/adc/test/test_radc/test_N2_radc_ea.py",
                    "pyscf/adc/test/test_radc/test_N2_radc_ip.py",
                ],
            },
            "2306": {
                "version": "2.6.2",
                "test_directory": [
                    "pyscf/fci/test/test_spin1.py",
                    "pyscf/fci/test/test_spin1_symm.py",
                ],
            },
            "2305": {
                "version": "2.6.2",
                "test_directory": ["pyscf/fci/test/test_direct_nosym.py"],
            },
            "2290": {
                "version": "2.6.2",
                "test_directory": ["pyscf/scf/test/test_addons.py"],
            },
            "2279": {
                "version": "2.6.2",
                "test_directory": [
                    "pyscf/tdscf/test/test_tdrks.py",
                    "pyscf/tdscf/test/test_tduks.py",
                ],
            },
            "2172": {
                "version": "2.5.0",
                "test_directory": [
                    "pyscf/pbc/dft/test/test_kgks.py",
                    "pyscf/pbc/dft/test/test_krks.py",
                    "pyscf/pbc/dft/test/test_kuks.py",
                ],
            },
            "2062": {
                "version": "2.4.0",
                "test_directory": [
                    "pyscf/fci/test/test_spin1_cyl_sym.py",
                    "pyscf/fci/test/test_spin1_symm.py",
                ],
            },
            "2050": {
                "version": "2.4.0",
                "test_directory": ["pyscf/fci/test/test_cistring.py"],
            },
            "2010": {
                "version": "2.5.0",
                "test_directory": [
                    "pyscf/dft/test/test_he.py",
                    "pyscf/dft/test/test_xc_deriv.py",
                ],
            },
            "1963": {
                "version": "2.5.0",
                "test_directory": ["pyscf/tools/test/test_molden.py"],
            },
            "1960": {
                "version": "2.5.0",
                "test_directory": ["pyscf/pbc/dft/test/test_gen_grid.py"],
            },
            "1947": {
                "version": "2.4.0",
                "test_directory": ["pyscf/pbc/df/test/test_rsdf.py"],
            },
            "1943": {
                "version": "2.4.0",
                "test_directory": ["pyscf/gto/test/test_mole.py"],
            },
            "1927": {
                "version": "2.4.0",
                "test_directory": ["pyscf/pbc/dft/test/test_krks_ksym.py"],
            },
            "1914": {
                "version": "2.4.0",
                "test_directory": ["pyscf/grad/test/test_casci.py"],
            },
            "1891": {
                "version": "2.3.0",
                "test_directory": ["pyscf/gto/test/test_ecp.py"],
            },
            "1869": {
                "version": "2.3.0",
                "test_directory": ["pyscf/mcscf/test/test_newton_casscf.py"],
            },
            "1845": {
                "version": "2.3.0",
                "test_directory": ["pyscf/fci/test/test_selected_ci.py"],
            },
            "1841": {
                "version": "2.6.2",
                "test_directory": ["pyscf/scf/test/test_uhf.py"],
            },
            "1821": {
                "version": "2.3.0",
                "test_directory": ["pyscf/pbc/gto/test/test_cell.py"],
            },
            "1803": {
                "version": "2.3.0",
                "test_directory": ["pyscf/lo/test/test_nao.py"],
            },
            "1773": {
                "version": "2.3.0",
                "test_directory": [
                    "pyscf/pbc/mp/test/test_ksym.py",
                    "pyscf/pbc/symm/test/test_spg.py",
                    "pyscf/pbc/tools/test/test_pbc.py",
                ],
            },
            "1654": {
                "version": "2.2.0",
                "test_directory": [
                    "pyscf/ci/test/test_cisd.py",
                    "pyscf/lib/test/test_linalg_helper.py",
                    "pyscf/mcscf/test/test_newton_casscf.py",
                ],
            },
            "1643": {
                "version": "2.2.0",
                "test_directory": ["pyscf/symm/test/test_geom.py"],
            },
            "1638": {
                "version": "2.2.0",
                "test_directory": [
                    "pyscf/scf/test/test_diis.py",
                    "pyscf/scf/test/test_rhf.py",
                ],
            },
            "1620": {
                "version": "2.1.1",
                "test_directory": ["pyscf/gto/test/test_mole.py"],
            },
            "1594": {
                "version": "2.1.1",
                "test_directory": ["pyscf/pbc/dft/test/test_krks_ksym.py"],
            },
            "1584": {
                "version": "2.1.1",
                "test_directory": ["pyscf/pbc/lib/test/test_kpts_ksymm.py"],
            },
            "1529": {
                "version": "2.1.1",
                "test_directory": [
                    "pyscf/fci/test/test_addons.py",
                    "pyscf/fci/test/test_spin0_symm.py",
                    "pyscf/fci/test/test_spin1_symm.py",
                    "pyscf/gto/test/test_mole.py",
                    "pyscf/mcscf/test/test_addons.py",
                    "pyscf/mcscf/test/test_casci.py",
                    "pyscf/mcscf/test/test_mc1step.py",
                    "pyscf/mcscf/test/test_n2.py",
                    "pyscf/mcscf/test/test_newton_casscf.py",
                    "pyscf/soscf/test/test_newton_ah.py",
                ],
            },
            "1450": {
                "version": "2.1.1",
                "test_directory": ["pyscf/ci/test/test_ucisd.py"],
            },
            "1441": {
                "version": "2.1.1",
                "test_directory": [
                    "pyscf/lib/test/test_numint_uniform_grid.py",
                    "pyscf/pbc/cc/test/test_eom_kgccsd.py",
                    "pyscf/pbc/cc/test/test_eom_kgccsd_diag.py",
                    "pyscf/pbc/cc/test/test_eom_krccsd.py",
                    "pyscf/pbc/cc/test/test_eom_kuccsd.py",
                    "pyscf/pbc/cc/test/test_kgccsd.py",
                    "pyscf/pbc/cc/test/test_krccsd.py",
                    "pyscf/pbc/df/test/test_df_jk.py",
                    "pyscf/pbc/df/test/test_gdf_builder.py",
                    "pyscf/pbc/df/test/test_mdf.py",
                    "pyscf/pbc/df/test/test_mdf_builder.py",
                    "pyscf/pbc/df/test/test_mdf_jk.py",
                    "pyscf/pbc/df/test/test_rsdf_scf.py",
                    "pyscf/pbc/dft/test/test_gen_grid.py",
                    "pyscf/pbc/dft/test/test_kgks.py",
                    "pyscf/pbc/dft/test/test_krkspu.py",
                    "pyscf/pbc/dft/test/test_kukspu.py",
                    "pyscf/pbc/dft/test/test_multigrid.py",
                    "pyscf/pbc/dft/test/test_numint.py",
                    "pyscf/pbc/dft/test/test_rks.py",
                    "pyscf/pbc/gto/test/test_cell.py",
                    "pyscf/pbc/mp/test/test_kpoint.py",
                    "pyscf/pbc/mp/test/test_padding.py",
                    "pyscf/pbc/scf/test/test_hf.py",
                    "pyscf/pbc/scf/test/test_khf.py",
                    "pyscf/pbc/scf/test/test_khf_ksym.py",
                    "pyscf/pbc/scf/test/test_rohf.py",
                    "pyscf/pbc/scf/test/test_uhf.py",
                    "pyscf/pbc/tools/make_test_cell.py",
                    "pyscf/pbc/tools/test/test_pbc.py",
                ],
            },
            "1426": {
                "version": "2.1.0",
                "test_directory": [
                    "pyscf/cc/test/test_dfccsd.py",
                    "pyscf/cc/test/test_eom_rccsd.py",
                    "pyscf/cc/test/test_eom_uccsd.py",
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
        
        if TEST_INDIVIDUAL_FILES:
            # Test individual files
            test_targets = test_dirs
        else:
            # Test directories only - extract unique directories
            test_directories = set()
            for test_path in test_dirs:
                if test_path.endswith('.py'):
                    # Extract directory from file path
                    test_directories.add('/'.join(test_path.split('/')[:-1]))
                else:
                    test_directories.add(test_path)
            test_targets = sorted(test_directories)
        
        if not test_dirs:
            raise ValueError(f"No test directories found for PR #{self.pr.number}")

        # Format test targets for pytest command - each target prefixed with /home/pyscf/
        pytest_targets = ' '.join(f'/home/pyscf/{target}' for target in test_targets)

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
python -m pytest {pytest_targets} --no-header -rA --tb=no -p no:cacheprovider
""".format(pr=self.pr, pytest_targets=pytest_targets),
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
python -m pytest {pytest_targets} --no-header -rA --tb=no -p no:cacheprovider
""".format(pr=self.pr, pytest_targets=pytest_targets),
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
python -m pytest {pytest_targets} --no-header -rA --tb=no -p no:cacheprovider

""".format(pr=self.pr, pytest_targets=pytest_targets),
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

        dockerfile_content = f"""
        FROM titouandu/pyscf-build:{pyscf_version}

        WORKDIR /home/pyscf

        RUN git fetch origin && \
            git fetch --no-tags origin "pull/{self.pr.number}/head:pr-{self.pr.number}" && \
            git checkout {self.pr.base.sha}

        RUN python -c "import pyscf; from pyscf import cc; print('✅ PySCF CC module import successful')"

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

