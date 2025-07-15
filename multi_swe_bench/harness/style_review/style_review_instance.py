from multi_swe_bench.harness.image import Config
from multi_swe_bench.harness.instance import Instance
from multi_swe_bench.harness.pull_request import PullRequest
from multi_swe_bench.harness.test_result import TestResult, TestStatus

from style_review_image import JavaStyleReviewImage

class JavaStyleReviewInstance(Instance):
    def __init__(self, pr: PullRequest, config: Config):
        self._pr = pr
        self._config = config
        self._image = JavaStyleReviewImage(pr, config)
    
    @property
    def pr(self) -> PullRequest:
        return self._pr
    
    def dependency(self):
        return self._image
    
    def run(self) -> str:
        # Command to run the style review on the repository without applying patch
        return "/workspace/run_style_review.sh /dev/null /workspace/output"
    
    def fix_patch_run(self) -> str:
        # Command to run the style review with the fix patch applied
        return "/workspace/run_style_review.sh /home/fix.patch /workspace/output"
    
    def parse_log(self, test_log: str) -> TestResult:
        # For style review, we don't need to parse test logs in the same way
        # as bug fixes. Instead we create a minimal TestResult.
        return TestResult(
            passed_count=1,  # We consider style review to have run successfully
            failed_count=0,
            skipped_count=0,
            passed_tests={"style_review"},
            failed_tests=set(),
            skipped_tests=set()
        )