#!/bin/bash

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

show_help() {
    echo -e "${BLUE}RMU API Attack - Release Creator${NC}"
    echo ""
    echo "Usage: $0 [version]"
    echo ""
    echo "Parameters:"
    echo "  version    Version to create (e.g.: 1.2.0, 2.0.0-beta.1)"
    echo ""
    echo "Options:"
    echo "  -h, --help     Show this help"
    echo "  -d, --dry-run  Show commands without executing"
    echo ""
    echo "Examples:"
    echo "  $0 1.2.0"
    echo "  $0 2.0.0-beta.1"
    echo "  $0 --dry-run 1.2.0"
    echo ""
    echo "The script will:"
    echo "  1. Verify that git flow is initialized"
    echo "  2. Check repository status"
    echo "  3. Create release branch from develop"
    echo "  4. Update version in configuration files"
    echo "  5. Finish release (merge to main and develop)"
    echo "  6. Create version tag"
    echo "  7. Push main, develop and tags"
}

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

execute_command() {
    local cmd="$1"
    local description="$2"
    
    if [ "$DRY_RUN" = true ]; then
        echo -e "${YELLOW}[DRY-RUN]${NC} $description"
        echo -e "${YELLOW}    →${NC} $cmd"
        return 0
    fi
    
    log_info "$description"
    echo -e "${YELLOW}    →${NC} $cmd"
    
    if eval "$cmd"; then
        log_success "Completed: $description"
        return 0
    else
        log_error "Failed: $description"
        return 1
    fi
}

validate_version() {
    local version="$1"
    if [[ ! "$version" =~ ^[0-9]+\.[0-9]+\.[0-9]+(-[a-zA-Z0-9\.-]+)?$ ]]; then
        log_error "Invalid version format: $version"
        log_error "Must follow semver format: x.y.z or x.y.z-suffix"
        exit 1
    fi
}

check_prerequisites() {
    log_info "Checking prerequisites..."
    # Check git
    if ! command -v git &> /dev/null; then
        log_error "git is not installed"
        exit 1
    fi
    
    # Check git flow
    if ! git flow version &> /dev/null; then
        log_error "git flow is not installed"
        log_error "Install with: apt-get install git-flow (Ubuntu) or brew install git-flow (macOS)"
        exit 1
    fi
    
    # Check that we are in a git repository
    if ! git rev-parse --git-dir &> /dev/null; then
        log_error "Not in a git repository"
        exit 1
    fi
    
    # Check that git flow is initialized
    if ! git config --get gitflow.branch.master &> /dev/null; then
        log_warning "Git flow is not initialized. Initializing..."
        execute_command "git flow init -d" "Initialize git flow with default configuration"
    fi
    
    log_success "Prerequisites verified"
}

# Function to check repository state
check_repository_state() {
    log_info "Checking repository state..."
    
    # Check that there are no uncommitted changes
    if ! git diff-index --quiet HEAD --; then
        log_error "There are uncommitted changes in the repository"
        log_error "Run 'git status' to see the changes"
        exit 1
    fi
    
    # Check that we are on develop
    current_branch=$(git branch --show-current)
    if [ "$current_branch" != "develop" ]; then
        log_warning "You are not on develop branch. Switching to develop..."
        execute_command "git checkout develop" "Switch to develop branch"
    fi
    
    # Update develop
    execute_command "git pull origin develop" "Update develop branch"
    log_success "Repository state verified"
}

# Function to check if version already exists
check_version_exists() {
    local version="$1"
    
    if git tag -l | grep -q "^v${version}$"; then
        log_error "Version v${version} already exists"
        log_error "Existing versions:"
        git tag -l --sort=-version:refname | head -10
        exit 1
    fi
}

# Function to update version files
update_version_files() {
    local version="$1"
    
    log_info "Updating version files..."
    
    # Update pyproject.toml
    if [ -f "pyproject.toml" ]; then
        execute_command "sed -i 's/^version = .*/version = \"${version}\"/' pyproject.toml" "Update version in pyproject.toml"
    fi
    
    # Update __init__.py if exists
    if [ -f "app/__init__.py" ]; then
        execute_command "sed -i 's/__version__ = .*/__version__ = \"${version}\"/' app/__init__.py" "Update version in app/__init__.py"
    fi
    
    # Create or update VERSION file
    execute_command "echo '${version}' > VERSION" "Create VERSION file"
    
    # Commit version changes
    execute_command "git add ." "Add version changes"
    execute_command "git commit -m 'chore: bump version to ${version}'" "Commit version changes"
}

# Main function to create release
create_release() {
    local version="$1"
    
    log_info "Starting release creation v${version}..."
    
    # Check prerequisites
    check_prerequisites
    
    # Check repository state
    check_repository_state
    
    # Check that version doesn't exist
    check_version_exists "$version"
    
    # Start release
    execute_command "git flow release start ${version}" "Start release branch"
    
    # Update version files
    update_version_files "$version"
    
    # Finish release
    execute_command "git flow release finish -m 'Release v${version}' ${version}" "Finish release"
    
    # Push all branches and tags
    execute_command "git push origin main" "Push main branch"
    execute_command "git push origin develop" "Push develop branch"
    execute_command "git push origin --tags" "Push tags"
    
    log_success "Release v${version} created successfully!"
    log_info "Tag created: v${version}"
    log_info "Updated branches: main, develop"
    log_info "To view the release: git tag -l | grep ${version}"
}

# Main function
main() {
    local version=""
    DRY_RUN=false
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -d|--dry-run)
                DRY_RUN=true
                shift
                ;;
            -*)
                log_error "Unknown option: $1"
                show_help
                exit 1
                ;;
            *)
                if [ -z "$version" ]; then
                    version="$1"
                else
                    log_error "Too many arguments"
                    show_help
                    exit 1
                fi
                shift
                ;;
        esac
    done
    
    # Check that version was provided
    if [ -z "$version" ]; then
        log_error "Must specify a version"
        show_help
        exit 1
    fi
    
    # Validate version format
    validate_version "$version"
    
    # Show summary
    echo -e "\n${BLUE}═══════════════════════════════════════${NC}"
    echo -e "${BLUE}  RMU API Attack - Release Creator${NC}"
    echo -e "${BLUE}═══════════════════════════════════════${NC}"
    echo -e "Version to create: ${GREEN}v${version}${NC}"
    echo -e "Dry-run mode: ${YELLOW}${DRY_RUN}${NC}"
    echo -e "Repository: ${BLUE}$(pwd)${NC}"
    echo -e "${BLUE}═══════════════════════════════════════${NC}\n"
    
    if [ "$DRY_RUN" = false ]; then
        echo -e "${YELLOW}Continue with release creation? [y/N]${NC}"
        read -r response
        if [[ ! "$response" =~ ^[yY]$ ]]; then
            log_info "Operation cancelled by user"
            exit 0
        fi
    fi
    create_release "$version"
}

main "$@"
