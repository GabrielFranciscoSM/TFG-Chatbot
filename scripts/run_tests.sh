#!/usr/bin/env bash
# ============================================================================
# run_tests.sh - Execute tests in Docker containers for each service
# ============================================================================
# Usage: ./scripts/run_tests.sh [service|all] [pytest_args...]
#
# Services:
#   chatbot    - Run chatbot service tests (tfg-chatbot container)
#   rag        - Run RAG service tests (rag-service container)
#   backend    - Run backend/gateway tests (tfg-gateway container)
#   math       - Run math service tests (math-service container)
#   all        - Run tests for all services
#
# Options:
#   --no-rebuild  Skip rebuilding containers (faster, but may miss code changes)
#
# Examples:
#   ./scripts/run_tests.sh all
#   ./scripts/run_tests.sh chatbot
#   ./scripts/run_tests.sh rag -k "test_embeddings"
#   ./scripts/run_tests.sh all --no-rebuild
# ============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Report directory
REPORT_DIR="$PROJECT_ROOT/test-reports"
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
REPORT_FILE="$REPORT_DIR/test-report_$TIMESTAMP.md"

# Results tracking
declare -A RESULTS
declare -A RAW_OUTPUT
TOTAL_PASSED=0
TOTAL_FAILED=0
TOTAL_ERRORS=0
REBUILD=true

# ============================================================================
# Helper Functions
# ============================================================================

print_header() {
    echo -e "\n${BLUE}════════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}\n"
}

print_section() {
    echo -e "\n${YELLOW}── $1 ──${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

setup_report_dir() {
    mkdir -p "$REPORT_DIR"
    echo "# Test Report - $TIMESTAMP" > "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    echo "Generated: $(date)" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
}

write_to_report() {
    echo "$1" >> "$REPORT_FILE"
}

# ============================================================================
# Container Management
# ============================================================================

rebuild_container() {
    local service="$1"
    local container_name="$2"
    
    if [[ "$REBUILD" != true ]]; then
        print_warning "Skipping rebuild (--no-rebuild flag)"
        return 0
    fi
    
    print_section "Rebuilding $service container"
    
    # Set INSTALL_DEV=true for dev dependencies (pytest, etc.)
    export INSTALL_DEV=true
    
    # Rebuild and restart the container
    docker compose build "$service" 2>&1 | tail -5
    docker compose up -d "$service" 2>&1
    
    # Wait for container to be ready
    echo "Waiting for $container_name to be ready..."
    sleep 3
    
    if docker compose ps --status running | grep -q "$container_name"; then
        print_success "$container_name is running"
    else
        print_error "$container_name failed to start"
        return 1
    fi
}

# ============================================================================
# Test Runners
# ============================================================================

run_chatbot_tests() {
    local extra_args="$*"
    print_section "Running Chatbot Tests (tfg-chatbot)"
    write_to_report "## Chatbot Tests"
    write_to_report ""
    
    rebuild_container "chatbot" "tfg-chatbot"
    
    local output
    local exit_code=0
    
    output=$(docker compose exec -T chatbot python -m pytest chatbot/tests/ \
        --tb=short \
        --no-header \
        -q \
        $extra_args 2>&1) || exit_code=$?
    
    echo "$output"
    RAW_OUTPUT["chatbot"]="$output"
    
    # Save to report
    write_to_report '```'
    write_to_report "$output"
    write_to_report '```'
    write_to_report ""
    
    # Parse results
    if echo "$output" | grep -qE "passed|failed|error"; then
        local passed=$(echo "$output" | grep -oE "[0-9]+ passed" | grep -oE "[0-9]+" || echo "0")
        local failed=$(echo "$output" | grep -oE "[0-9]+ failed" | grep -oE "[0-9]+" || echo "0")
        local errors=$(echo "$output" | grep -oE "[0-9]+ error" | grep -oE "[0-9]+" || echo "0")
        
        RESULTS["chatbot"]="passed:${passed:-0},failed:${failed:-0},errors:${errors:-0}"
        TOTAL_PASSED=$((TOTAL_PASSED + ${passed:-0}))
        TOTAL_FAILED=$((TOTAL_FAILED + ${failed:-0}))
        TOTAL_ERRORS=$((TOTAL_ERRORS + ${errors:-0}))
    else
        RESULTS["chatbot"]="passed:0,failed:0,errors:1"
        TOTAL_ERRORS=$((TOTAL_ERRORS + 1))
    fi
    
    return $exit_code
}

run_rag_tests() {
    local extra_args="$*"
    print_section "Running RAG Service Tests (rag-service)"
    write_to_report "## RAG Service Tests"
    write_to_report ""
    
    rebuild_container "rag_service" "rag-service"
    
    local output
    local exit_code=0
    
    output=$(docker compose exec -T rag_service python -m pytest rag_service/tests/ \
        --tb=short \
        --no-header \
        -q \
        $extra_args 2>&1) || exit_code=$?
    
    echo "$output"
    RAW_OUTPUT["rag"]="$output"
    
    # Save to report
    write_to_report '```'
    write_to_report "$output"
    write_to_report '```'
    write_to_report ""
    
    # Parse results
    if echo "$output" | grep -qE "passed|failed|error"; then
        local passed=$(echo "$output" | grep -oE "[0-9]+ passed" | grep -oE "[0-9]+" || echo "0")
        local failed=$(echo "$output" | grep -oE "[0-9]+ failed" | grep -oE "[0-9]+" || echo "0")
        local errors=$(echo "$output" | grep -oE "[0-9]+ error" | grep -oE "[0-9]+" || echo "0")
        
        RESULTS["rag"]="passed:${passed:-0},failed:${failed:-0},errors:${errors:-0}"
        TOTAL_PASSED=$((TOTAL_PASSED + ${passed:-0}))
        TOTAL_FAILED=$((TOTAL_FAILED + ${failed:-0}))
        TOTAL_ERRORS=$((TOTAL_ERRORS + ${errors:-0}))
    else
        RESULTS["rag"]="passed:0,failed:0,errors:1"
        TOTAL_ERRORS=$((TOTAL_ERRORS + 1))
    fi
    
    return $exit_code
}

run_backend_tests() {
    local extra_args="$*"
    print_section "Running Backend Tests (tfg-gateway)"
    write_to_report "## Backend Tests"
    write_to_report ""
    
    rebuild_container "backend" "tfg-gateway"
    
    local output
    local exit_code=0
    
    output=$(docker compose exec -T backend python -m pytest backend/tests/ \
        --tb=short \
        --no-header \
        -q \
        $extra_args 2>&1) || exit_code=$?
    
    echo "$output"
    RAW_OUTPUT["backend"]="$output"
    
    # Save to report
    write_to_report '```'
    write_to_report "$output"
    write_to_report '```'
    write_to_report ""
    
    # Parse results
    if echo "$output" | grep -qE "passed|failed|error"; then
        local passed=$(echo "$output" | grep -oE "[0-9]+ passed" | grep -oE "[0-9]+" || echo "0")
        local failed=$(echo "$output" | grep -oE "[0-9]+ failed" | grep -oE "[0-9]+" || echo "0")
        local errors=$(echo "$output" | grep -oE "[0-9]+ error" | grep -oE "[0-9]+" || echo "0")
        
        RESULTS["backend"]="passed:${passed:-0},failed:${failed:-0},errors:${errors:-0}"
        TOTAL_PASSED=$((TOTAL_PASSED + ${passed:-0}))
        TOTAL_FAILED=$((TOTAL_FAILED + ${failed:-0}))
        TOTAL_ERRORS=$((TOTAL_ERRORS + ${errors:-0}))
    else
        RESULTS["backend"]="passed:0,failed:0,errors:1"
        TOTAL_ERRORS=$((TOTAL_ERRORS + 1))
    fi
    
    return $exit_code
}

run_math_tests() {
    local extra_args="$*"
    print_section "Running Math Service Tests (math-service)"
    write_to_report "## Math Service Tests"
    write_to_report ""
    
    rebuild_container "math_service" "math-service"
    
    local output
    local exit_code=0
    
    output=$(docker compose exec -T math_service python -m pytest math_service/tests/ \
        --tb=short \
        --no-header \
        -q \
        $extra_args 2>&1) || exit_code=$?
    
    echo "$output"
    RAW_OUTPUT["math"]="$output"
    
    # Save to report
    write_to_report '```'
    write_to_report "$output"
    write_to_report '```'
    write_to_report ""
    
    # Parse results
    if echo "$output" | grep -qE "passed|failed|error"; then
        local passed=$(echo "$output" | grep -oE "[0-9]+ passed" | grep -oE "[0-9]+" || echo "0")
        local failed=$(echo "$output" | grep -oE "[0-9]+ failed" | grep -oE "[0-9]+" || echo "0")
        local errors=$(echo "$output" | grep -oE "[0-9]+ error" | grep -oE "[0-9]+" || echo "0")
        
        RESULTS["math"]="passed:${passed:-0},failed:${failed:-0},errors:${errors:-0}"
        TOTAL_PASSED=$((TOTAL_PASSED + ${passed:-0}))
        TOTAL_FAILED=$((TOTAL_FAILED + ${failed:-0}))
        TOTAL_ERRORS=$((TOTAL_ERRORS + ${errors:-0}))
    else
        RESULTS["math"]="passed:0,failed:0,errors:1"
        TOTAL_ERRORS=$((TOTAL_ERRORS + 1))
    fi
    
    return $exit_code
}

# ============================================================================
# Summary Report
# ============================================================================

print_summary() {
    print_header "Test Summary Report"
    write_to_report "## Summary"
    write_to_report ""
    write_to_report "| Service | Passed | Failed | Errors |"
    write_to_report "|---------|--------|--------|--------|"
    
    echo -e "Service Results:"
    echo -e "────────────────────────────────────────────"
    
    for service in "${!RESULTS[@]}"; do
        local result="${RESULTS[$service]}"
        local passed=$(echo "$result" | grep -oP 'passed:\K[0-9]+')
        local failed=$(echo "$result" | grep -oP 'failed:\K[0-9]+')
        local errors=$(echo "$result" | grep -oP 'errors:\K[0-9]+')
        
        local status_icon="✓"
        local status_color="$GREEN"
        if [[ "$failed" -gt 0 ]] || [[ "$errors" -gt 0 ]]; then
            status_icon="✗"
            status_color="$RED"
        fi
        
        printf "  ${status_color}${status_icon}${NC} %-12s │ " "$service"
        echo -e "${GREEN}${passed} passed${NC}, ${RED}${failed} failed${NC}, ${YELLOW}${errors} errors${NC}"
        
        write_to_report "| $service | $passed | $failed | $errors |"
    done
    
    echo -e "────────────────────────────────────────────"
    echo -e "  Total:       │ ${GREEN}${TOTAL_PASSED} passed${NC}, ${RED}${TOTAL_FAILED} failed${NC}, ${YELLOW}${TOTAL_ERRORS} errors${NC}"
    echo ""
    
    write_to_report "| **Total** | **${TOTAL_PASSED}** | **${TOTAL_FAILED}** | **${TOTAL_ERRORS}** |"
    write_to_report ""
    
    if [[ $TOTAL_FAILED -eq 0 ]] && [[ $TOTAL_ERRORS -eq 0 ]]; then
        print_success "All tests passed! 🎉"
        write_to_report "> ✅ **All tests passed!**"
        echo ""
        echo -e "Report saved to: ${BLUE}$REPORT_FILE${NC}"
        return 0
    else
        print_error "Some tests failed. See details above."
        write_to_report "> ❌ **Some tests failed. See details above.**"
        echo ""
        echo -e "Report saved to: ${BLUE}$REPORT_FILE${NC}"
        return 1
    fi
}

# ============================================================================
# Main
# ============================================================================

main() {
    cd "$PROJECT_ROOT"
    
    if [[ $# -eq 0 ]]; then
        echo "Usage: $0 [chatbot|rag|backend|all] [--no-rebuild] [pytest_args...]"
        echo ""
        echo "Examples:"
        echo "  $0 all              # Run all tests (with rebuild)"
        echo "  $0 chatbot          # Run chatbot tests only"
        echo "  $0 rag --no-rebuild # Run RAG tests without rebuilding"
        echo "  $0 all -k embed     # Run all tests matching 'embed'"
        exit 1
    fi
    
    local service="$1"
    shift
    
    # Check for --no-rebuild flag
    local extra_args=""
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --no-rebuild)
                REBUILD=false
                shift
                ;;
            *)
                extra_args="$extra_args $1"
                shift
                ;;
        esac
    done
    
    # Setup report directory and file
    setup_report_dir
    
    print_header "Docker Test Runner"
    echo "Service: $service"
    echo "Rebuild: $REBUILD"
    [[ -n "$extra_args" ]] && echo "Extra args:$extra_args"
    
    write_to_report "**Service:** $service"
    write_to_report "**Rebuild:** $REBUILD"
    write_to_report ""
    
    local exit_code=0
    
    case "$service" in
        chatbot)
            run_chatbot_tests $extra_args || exit_code=1
            ;;
        rag)
            run_rag_tests $extra_args || exit_code=1
            ;;
        backend)
            run_backend_tests $extra_args || exit_code=1
            ;;
        math)
            run_math_tests $extra_args || exit_code=1
            ;;
        all)
            run_chatbot_tests $extra_args || exit_code=1
            run_rag_tests $extra_args || exit_code=1
            run_backend_tests $extra_args || exit_code=1
            run_math_tests $extra_args || exit_code=1
            ;;
        *)
            print_error "Unknown service: $service"
            echo "Valid services: chatbot, rag, backend, math, all"
            exit 1
            ;;
    esac
    
    print_summary
    exit $exit_code
}

main "$@"
