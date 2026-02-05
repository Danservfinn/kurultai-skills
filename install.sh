#!/bin/bash
#
# Kurultai Installation Script
# Installs the Kurultai skills marketplace for Claude Code
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
INSTALL_DIR="${HOME}/.kurultai"
SKILLS_DIR="${INSTALL_DIR}/skills"
CLI_VERSION="0.1.0"

# Print functions
print_header() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                                                              ║"
    echo "║   ██╗  ██╗██╗   ██╗██████╗ ██╗   ██╗██╗     ████████╗ █████╗ ██╗"
    echo "║   ██║ ██╔╝██║   ██║██╔══██╗██║   ██║██║     ╚══██╔══╝██╔══██╗██║"
    echo "║   █████╔╝ ██║   ██║██████╔╝██║   ██║██║        ██║   ███████║██║"
    echo "║   ██╔═██╗ ██║   ██║██╔══██╗██║   ██║██║        ██║   ██╔══██║██║"
    echo "║   ██║  ██╗╚██████╔╝██║  ██║╚██████╔╝███████╗   ██║   ██║  ██║██║"
    echo "║   ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝"
    echo "║                                                              ║"
    echo "║          Skills Marketplace for Claude Code                  ║"
    echo "║                                                              ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    print_info "Checking prerequisites..."

    # Check for git
    if ! command -v git &> /dev/null; then
        print_error "git is required but not installed. Please install git first."
        exit 1
    fi

    # Check for Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is required but not installed. Please install Python 3 first."
        exit 1
    fi

    # Check for Claude Code
    if ! command -v claude &> /dev/null; then
        print_warning "Claude Code CLI not found. You'll need to install it separately."
        print_info "Visit: https://claude.ai/code"
    fi

    print_success "Prerequisites check passed"
}

# Create directory structure
setup_directories() {
    print_info "Setting up directory structure..."

    mkdir -p "${SKILLS_DIR}"
    mkdir -p "${INSTALL_DIR}/cache"
    mkdir -p "${INSTALL_DIR}/config"

    print_success "Directories created at ${INSTALL_DIR}"
}

# Install CLI tool
install_cli() {
    print_info "Installing Kurultai CLI..."

    # Create virtual environment if it doesn't exist
    if [ ! -d "${INSTALL_DIR}/venv" ]; then
        python3 -m venv "${INSTALL_DIR}/venv"
    fi

    # Activate virtual environment
    source "${INSTALL_DIR}/venv/bin/activate"

    # Install kurultai package
    pip install --quiet kurultai==${CLI_VERSION} 2>/dev/null || {
        print_warning "Could not install from PyPI, installing from source..."
        pip install --quiet git+https://github.com/kurultai/kurultai-cli.git
    }

    # Create wrapper script
    cat > "${INSTALL_DIR}/kurultai" << 'EOF'
#!/bin/bash
source "${HOME}/.kurultai/venv/bin/activate"
kurultai "$@"
EOF
    chmod +x "${INSTALL_DIR}/kurultai"

    print_success "CLI installed"
}

# Add to PATH
add_to_path() {
    print_info "Adding Kurultai to PATH..."

    SHELL_RC=""
    if [[ "$SHELL" == *"zsh"* ]]; then
        SHELL_RC="${HOME}/.zshrc"
    elif [[ "$SHELL" == *"bash"* ]]; then
        SHELL_RC="${HOME}/.bashrc"
    else
        SHELL_RC="${HOME}/.profile"
    fi

    # Check if already in PATH
    if ! grep -q "${INSTALL_DIR}" "$SHELL_RC" 2>/dev/null; then
        echo "" >> "$SHELL_RC"
        echo "# Kurultai Skills Marketplace" >> "$SHELL_RC"
        echo "export PATH=\"${INSTALL_DIR}:\$PATH\"" >> "$SHELL_RC"
        print_success "Added to PATH in ${SHELL_RC}"
        print_info "Please run: source ${SHELL_RC}"
    else
        print_info "Already in PATH"
    fi
}

# Install core skills
install_core_skills() {
    print_info "Installing core horde skills..."

    source "${INSTALL_DIR}/venv/bin/activate"

    # Install horde-swarm (the engine)
    print_info "Installing horde-swarm (core engine)..."
    kurultai install github.com/kurultai/skills/horde-swarm --silent || {
        print_warning "Could not install horde-swarm, skipping..."
    }

    # Install other core skills
    CORE_SKILLS=(
        "horde-brainstorming"
        "horde-plan"
        "horde-implement"
        "horde-learn"
        "horde-gate-testing"
    )

    for skill in "${CORE_SKILLS[@]}"; do
        print_info "Installing ${skill}..."
        kurultai install "github.com/kurultai/skills/${skill}" --silent 2>/dev/null || {
            print_warning "Could not install ${skill}, skipping..."
        }
    done

    print_success "Core skills installed"
}

# Create initial configuration
create_config() {
    print_info "Creating initial configuration..."

    cat > "${INSTALL_DIR}/config/kurultai.yaml" << EOF
# Kurultai Configuration
version: "1.0.0"

# Registry settings
registry:
  url: "https://kurult.ai/registry.json"
  auto_update: true
  channel: stable  # stable | beta | canary

# Installation settings
install:
  default_source: "github.com/kurultai/skills"
  auto_resolve_deps: true
  verify_signatures: true

# Security settings
security:
  sandbox_skills: true
  max_subagents: 10
  allowed_hosts: []
  blocked_hosts: []

# Telemetry (opt-in)
telemetry:
  enabled: false
  anonymize: true

# Default skill configurations
skills:
  horde-swarm:
    max_agents: 4
    default_timeout: 300
EOF

    print_success "Configuration created"
}

# Print next steps
print_next_steps() {
    echo ""
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                                                              ║${NC}"
    echo -e "${GREEN}║   Installation Complete!                                     ║${NC}"
    echo -e "${GREEN}║                                                              ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "Next steps:"
    echo ""
    echo "  1. Reload your shell or run: source ~/.bashrc (or ~/.zshrc)"
    echo ""
    echo "  2. Verify installation:"
    echo "     kurultai --version"
    echo ""
    echo "  3. Discover available skills:"
    echo "     kurultai search"
    echo ""
    echo "  4. Install a skill:"
    echo "     kurultai install horde-swarm"
    echo ""
    echo "  5. Use a skill in Claude Code:"
    echo "     /claude use horde-swarm 'Your task here'"
    echo ""
    echo "Documentation: https://github.com/kurultai/kurultai#readme"
    echo "Community: https://discord.gg/kurultai"
    echo ""
}

# Main installation flow
main() {
    print_header

    print_info "Starting Kurultai installation..."
    print_info "Install directory: ${INSTALL_DIR}"
    echo ""

    check_prerequisites
    setup_directories
    install_cli
    add_to_path
    install_core_skills
    create_config

    print_next_steps
}

# Run main function
main "$@"
