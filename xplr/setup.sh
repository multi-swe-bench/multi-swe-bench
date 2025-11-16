#!/bin/bash
# Multi-SWE-bench Integration Test - Automated Setup Script
# This script sets up the environment and runs the integration test

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
print_header() {
    echo -e "\n${BLUE}======================================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}======================================================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${YELLOW}ℹ${NC} $1"
}

# Main setup
print_header "Multi-SWE-bench Integration Test - Automated Setup"

# Step 0: Check prerequisites
print_header "Step 0: Checking Prerequisites"

# Check Python version
if command -v python3.10 &> /dev/null; then
    PYTHON_CMD="python3.10"
elif command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    PYTHON_VERSION=$(python3 --version | awk '{print $2}')
    MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
    if [ "$MAJOR" -lt 3 ] || { [ "$MAJOR" -eq 3 ] && [ "$MINOR" -lt 10 ]; }; then
        print_error "Python >= 3.10 required, found $PYTHON_VERSION"
        exit 1
    fi
else
    print_error "Python not found. Please install Python >= 3.10"
    exit 1
fi
print_success "Python found: $($PYTHON_CMD --version)"

# Check Git
if ! command -v git &> /dev/null; then
    print_error "Git not found. Please install Git"
    exit 1
fi
print_success "Git found: $(git --version)"

# Navigate to project root
cd "$(dirname "$0")/.." || exit 1
PROJECT_ROOT=$(pwd)
print_success "Project root: $PROJECT_ROOT"

# Step 1: Check/Install uv
print_header "Step 1: Setting Up Package Manager"

if command -v uv &> /dev/null; then
    print_success "uv already installed: $(uv --version)"
    USE_UV=true
else
    print_info "uv not found. Would you like to install it? (recommended for faster setup)"
    print_info "Alternatively, we can use pip (slower but works everywhere)"
    read -p "Install uv? (y/n, default=y): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
        print_info "Installing uv..."
        curl -LsSf https://astral.sh/uv/install.sh | sh
        export PATH="$HOME/.local/bin:$PATH"
        if command -v uv &> /dev/null; then
            print_success "uv installed successfully: $(uv --version)"
            USE_UV=true
        else
            print_error "uv installation failed. Falling back to pip"
            USE_UV=false
        fi
    else
        print_info "Using pip for installation"
        USE_UV=false
    fi
fi

# Step 2: Create Virtual Environment
print_header "Step 2: Creating Virtual Environment"

if [ -d ".venv" ]; then
    print_info "Virtual environment already exists at .venv"
    read -p "Remove and recreate? (y/n, default=n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Removing existing virtual environment..."
        rm -rf .venv
        if [ "$USE_UV" = true ]; then
            uv venv
        else
            $PYTHON_CMD -m venv .venv
        fi
        print_success "Virtual environment recreated"
    else
        print_info "Using existing virtual environment"
    fi
else
    if [ "$USE_UV" = true ]; then
        uv venv
    else
        $PYTHON_CMD -m venv .venv
    fi
    print_success "Virtual environment created at .venv"
fi

# Activate virtual environment
source .venv/bin/activate
print_success "Virtual environment activated"

# Step 3: Install Dependencies
print_header "Step 3: Installing Dependencies"

print_info "Installing Multi-SWE-bench and dependencies..."
if [ "$USE_UV" = true ]; then
    uv pip install -e .
else
    pip install --upgrade pip
    pip install -e .
fi

print_success "Dependencies installed successfully"

# Verify installation
if python -c "import multi_swe_bench" 2>/dev/null; then
    print_success "Multi-SWE-bench package verified"
else
    print_error "Multi-SWE-bench installation verification failed"
    exit 1
fi

# Step 4: Display Installation Summary
print_header "Step 4: Installation Summary"

echo "Python: $($PYTHON_CMD --version)"
echo "Virtual Environment: $PROJECT_ROOT/.venv"
echo "Package Manager: $([ "$USE_UV" = true ] && echo "uv" || echo "pip")"
echo ""
echo "Installed Packages:"
pip list | grep -E "(multi-swe-bench|docker|gitpython|PyGithub|pytest)" || true

# Step 5: Run Integration Test
print_header "Step 5: Running Integration Test"

print_info "Executing test_msb_workflow.py..."
echo ""

if python xplr/test_msb_workflow.py; then
    print_header "✅ Setup and Testing Complete!"

    echo ""
    echo -e "${GREEN}All systems operational!${NC}"
    echo ""
    echo "Generated files:"
    echo "  • xplr/test_workflow_config.json - Instance configuration"
    echo "  • xplr/IMPLEMENTATION_SUMMARY.md - Detailed documentation"
    echo ""
    echo "To run the test again:"
    echo "  source .venv/bin/activate"
    echo "  python xplr/test_msb_workflow.py"
    echo ""
    echo "Next steps:"
    echo "  1. Read xplr/setup.md for manual reproduction instructions"
    echo "  2. Read xplr/IMPLEMENTATION_SUMMARY.md for implementation details"
    echo "  3. Collect real PR data: python -m multi_swe_bench.collect.get_pipeline"
    echo ""
else
    print_error "Integration test failed!"
    echo ""
    echo "Troubleshooting steps:"
    echo "  1. Check xplr/setup.md for manual setup instructions"
    echo "  2. Verify all dependencies: pip list"
    echo "  3. Check Python version: python --version (must be >= 3.10)"
    echo "  4. Review error output above"
    echo ""
    exit 1
fi

print_header "Setup Complete - Environment Ready"

echo ""
echo "Virtual environment is activated. To deactivate, run:"
echo "  deactivate"
echo ""
echo "To activate later:"
echo "  source .venv/bin/activate"
echo ""
