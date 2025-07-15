from multi_swe_bench.harness.image import Config, File, Image
from multi_swe_bench.harness.pull_request import PullRequest


class JavaStyleReviewImage(Image):
    def __init__(self, pr: PullRequest, config: Config):
        self._pr = pr
        self._config = config
    
    @property
    def pr(self) -> PullRequest:
        return self._pr
    
    @pr.setter
    def pr(self, value: PullRequest):
        self._pr = value
    
    @property
    def config(self) -> Config:
        return self._config
    
    @config.setter
    def config(self, value: Config):
        self._config = value
        
    def dependency(self) -> str:
        # Return base Java image
        return "openjdk:17-slim"
    
    def image_tag(self) -> str:
        return f"style-review-{self.pr.number}"
    
    def workdir(self) -> str:
        return f"style-review-{self.pr.number}"
    
    def files(self) -> list[File]:
        # Include Checkstyle configuration and any utility scripts
        return [
            File(
                dir="",
                name="checkstyle.xml",
                content=self._get_checkstyle_config()
            ),
            File(
                dir="",
                name="run_style_review.sh",
                content=self._get_style_review_script()
            )
        ]
    
    def dockerfile(self) -> str:
        # Create a Dockerfile that installs Checkstyle and sets up environment
        return f"""FROM {self.dependency()}
{self.global_env}

# Install necessary tools
RUN apt-get update && apt-get install -y wget unzip git jq

# Install Checkstyle
RUN wget -q https://github.com/checkstyle/checkstyle/releases/download/checkstyle-10.12.1/checkstyle-10.12.1-all.jar -O /usr/local/lib/checkstyle.jar

# Set up working directory
WORKDIR /workspace

# Copy configuration files
COPY checkstyle.xml /workspace/
COPY run_style_review.sh /workspace/
RUN chmod +x /workspace/run_style_review.sh

{self.clear_env}
"""
    
    def _get_checkstyle_config(self) -> str:
        # Return a standard Java checkstyle config
        return """<?xml version="1.0"?>
<!DOCTYPE module PUBLIC "-//Checkstyle//DTD Checkstyle Configuration 1.3//EN" "https://checkstyle.org/dtds/configuration_1_3.dtd">
<module name="Checker">
    <property name="severity" value="error"/>
    <module name="TreeWalker">
        <!-- Basic style checks -->
        <module name="ConstantName"/>
        <module name="LocalVariableName"/>
        <module name="MemberName"/>
        <module name="MethodName"/>
        <module name="PackageName"/>
        <module name="ParameterName"/>
        <module name="StaticVariableName"/>
        <module name="TypeName"/>
        
        <!-- Code quality checks -->
        <module name="AvoidStarImport"/>
        <module name="IllegalImport"/>
        <module name="RedundantImport"/>
        <module name="UnusedImports"/>
        <module name="MethodLength"/>
        <module name="ParameterNumber"/>
        <module name="EmptyBlock"/>
        <module name="NeedBraces"/>
        <module name="LeftCurly"/>
        <module name="RightCurly"/>
        <module name="WhitespaceAround"/>
        <module name="WhitespaceAfter"/>
        <module name="NoWhitespaceAfter"/>
        <module name="NoWhitespaceBefore"/>
        <module name="OperatorWrap"/>
        <module name="ParenPad"/>
        <module name="TypecastParenPad"/>
        <module name="ModifierOrder"/>
        <module name="RedundantModifier"/>
        <module name="AvoidNestedBlocks"/>
        <module name="EmptyStatement"/>
        <module name="EqualsHashCode"/>
        <module name="HiddenField"/>
        <module name="IllegalInstantiation"/>
        <module name="MagicNumber"/>
        <module name="MissingSwitchDefault"/>
        <module name="SimplifyBooleanExpression"/>
        <module name="SimplifyBooleanReturn"/>
        <module name="FinalClass"/>
        <module name="HideUtilityClassConstructor"/>
        <module name="InterfaceIsType"/>
        <module name="VisibilityModifier"/>
        <module name="ArrayTypeStyle"/>
        <module name="TodoComment"/>
        <module name="UpperEll"/>
    </module>
    
    <!-- File-level checks -->
    <module name="FileTabCharacter"/>
    <module name="NewlineAtEndOfFile"/>
</module>
"""
    
    def _get_style_review_script(self) -> str:
        # Script to run Checkstyle on Java files and output results in JSON format
        return """#!/bin/bash
set -e

# Function to apply patch and run Checkstyle
run_style_review() {
    local patch_file="$1"
    local output_dir="$2"
    
    # Create output directory
    mkdir -p "$output_dir"
    
    # Apply the patch
    if [ -f "$patch_file" ]; then
        git apply "$patch_file" || {
            echo "Error applying patch" > "$output_dir/error.log"
            return 1
        }
    else
        echo "No patch file found at $patch_file" > "$output_dir/error.log"
        return 1
    fi
    
    # Find all modified Java files
    modified_files=$(git diff --name-only HEAD | grep -E '\\.java$' || true)
    
    if [ -z "$modified_files" ]; then
        echo '{
            "global_score": 10.0,
            "total_errors": 0,
            "total_warnings": 0
        }' > "$output_dir/style_report.json"
        echo "[]" > "$output_dir/style_errors.json"
        return 0
    fi
    
    # Create temporary directory for intermediate files
    temp_dir=$(mktemp -d)
    trap 'rm -rf "$temp_dir"' EXIT
    
    # Initialize error report array
    echo "[]" > "$output_dir/style_errors.json"
    
    # Initialize counters
    total_errors=0
    total_files=0
    
    # Process each file
    for file in $modified_files; do
        [ -z "$file" ] && continue
        [ ! -f "$file" ] && continue
        
        total_files=$((total_files + 1))
        
        # Run Checkstyle and capture output
        java -jar /usr/local/lib/checkstyle.jar -c /workspace/checkstyle.xml "$file" -f xml > "$temp_dir/checkstyle.xml" 2>/dev/null || true
        
        # Convert XML to JSON for easier processing
        java -cp /usr/local/lib/checkstyle.jar com.puppycrawl.tools.checkstyle.Main -c /workspace/checkstyle.xml "$file" > "$temp_dir/checkstyle.txt" 2>/dev/null || true
        
        # Count errors
        file_errors=$(grep -c "\\[ERROR\\]" "$temp_dir/checkstyle.txt" || echo 0)
        total_errors=$((total_errors + file_errors))
        
        # Calculate file score (10 - number of errors, minimum 0)
        file_score=$(echo "scale=1; 10 - $file_errors * 0.5" | bc)
        if (( $(echo "$file_score < 0" | bc -l) )); then
            file_score="0.0"
        fi
        
        # Extract error messages
        error_messages=$(grep "\\[ERROR\\]" "$temp_dir/checkstyle.txt" | sed -e 's/^.*\[ERROR\] //' || echo "")
        
        # Create file report JSON
        file_report="{
            \"file\": \"$file\",
            \"score\": $file_score,
            \"error_count\": $file_errors,
            \"messages\": ["
        
        # Add error messages
        first=true
        while IFS= read -r message; do
            [ -z "$message" ] && continue
            
            if $first; then
                first=false
            else
                file_report+=","
            fi
            
            # Extract line number and message
            if [[ "$message" =~ ^([0-9]+):([0-9]+):\ (.*) ]]; then
                line="${BASH_REMATCH[1]}"
                column="${BASH_REMATCH[2]}"
                msg="${BASH_REMATCH[3]}"
                file_report+="{\"line\": $line, \"column\": $column, \"type\": \"error\", \"message\": \"${msg//\"/\\\"}\", \"source\": \"checkstyle\"}"
            else
                file_report+="{\"line\": 0, \"column\": 0, \"type\": \"error\", \"message\": \"${message//\"/\\\"}\", \"source\": \"checkstyle\"}"
            fi
        done <<< "$error_messages"
        
        file_report+="]},"
        
        # Append to main report (replacing the closing bracket with the new entry and a closing bracket)
        jq -s '.[0] + [.[1]]' "$output_dir/style_errors.json" <(echo "${file_report%?}") > "$temp_dir/new_errors.json"
        mv "$temp_dir/new_errors.json" "$output_dir/style_errors.json"
    done
    
    # Generate final summary
    global_score=10.0
    if [ "$total_files" -gt 0 ]; then
        global_score=$(echo "scale=1; 10 - ($total_errors / $total_files) * 0.5" | bc)
        if (( $(echo "$global_score < 0" | bc -l) )); then
            global_score="0.0"
        fi
    fi
    
    echo "{
        \"global_score\": $global_score,
        \"total_errors\": $total_errors,
        \"total_warnings\": 0
    }" > "$output_dir/style_report.json"
    
    return 0
}

# Main execution
if [ $# -lt 2 ]; then
    echo "Usage: $0 <patch_file> <output_dir>"
    exit 1
fi

run_style_review "$1" "$2"
"""