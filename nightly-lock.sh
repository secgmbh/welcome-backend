#!/bin/bash
# Nightly Improvements Lock Mechanism
# Ensures only one run at a time within the time window

LOCK_FILE="/tmp/nightly-improvements.lock"
LOCK_TIMEOUT=3600  # 1 hour
WORKING_DIR="/data/.openclaw/workspace"
TIMEZONE="Europe/Berlin"

# Check if we're in the valid time window (22:30 - 04:00)
check_time_window() {
    local current_hour=$(date +%H)
    local current_min=$(date +%M)
    local current_time=$((current_hour * 60 + current_min))
    
    # 22:30 = 1350 minutes, 04:00 = 240 minutes
    local start_time=1350
    local end_time=240
    
    if [[ $current_time -ge $start_time ]] || [[ $current_time -lt $end_time ]]; then
        return 0  # Inside window
    else
        return 1  # Outside window
    fi
}

# Try to acquire lock
acquire_lock() {
    if [[ -f "$LOCK_FILE" ]]; then
        local lock_age=$(( $(date +%s) - $(stat -c %Y "$LOCK_FILE" 2>/dev/null || echo 0) ))
        if [[ $lock_age -gt $LOCK_TIMEOUT ]]; then
            # Lock expired, remove it
            rm -f "$LOCK_FILE"
        else
            echo "Lock still active (age: ${lock_age}s), skipping..."
            return 1
        fi
    fi
    
    echo $$ > "$LOCK_FILE"
    trap 'rm -f "$LOCK_FILE"' EXIT
    return 0
}

# Main execution
main() {
    # Check time window
    if ! check_time_window; then
        echo "Outside time window (22:30-04:00), stopping..."
        exit 0
    fi
    
    # Try to acquire lock
    if ! acquire_lock; then
        exit 0
    fi
    
    echo "Nightly improvements started..."
    echo "Current time: $(date '+%Y-%m-%d %H:%M:%S %Z')"
    echo "Active window: 22:30-04:00"
    echo ""
    
    # Process Backend
    process_backend
    
    # Process Frontend (check if directory exists)
    if [[ -d "$WORKING_DIR/welcome-frontend" ]]; then
        process_frontend
    else
        echo "=== Frontend directory not found, skipping ==="
    fi
    
    echo ""
    echo "Nightly improvements completed!"
}

process_backend() {
    echo "=== Processing Backend (welcome-backend) ==="
    cd "$WORKING_DIR/welcome-backend"
    
    # Check branch
    local current_branch=$(git branch --show-current)
    echo "Current branch: $current_branch"
    
    # Checkout nightly-improvements if on main
    if [[ "$current_branch" == "main" || "$current_branch" == "master" ]]; then
        git checkout nightly-improvements 2>/dev/null || {
            echo "Creating nightly-improvements branch..."
            git checkout -b nightly-improvements
        }
    fi
    
    # Pull latest
    git pull origin nightly-improvements 2>/dev/null || echo "No remote nightly-improvements branch"
    
    # Task 1: Cleanup temp files
    find . -name "*.tmp" -o -name "*.log" -o -name "*.pyc" -o -name "__pycache__" 2>/dev/null | xargs rm -rf 2>/dev/null
    echo "✓ Cleanup temp files"
    
    # Task 2: Check TODOs
    local todo_count=$(grep -r "TODO\|FIXME" backend/ --include="*.py" 2>/dev/null | wc -l)
    echo "  Backend TODOs: $todo_count"
    
    # Task 3: Check print statements
    local print_count=$(grep -r "^\s*print(" backend/ --include="*.py" 2>/dev/null | wc -l)
    if [[ $print_count -gt 0 ]]; then
        echo "  ⚠️  Found $print_count print() statements"
    else
        echo "  ✓ No print() statements in backend"
    fi
    
    # Task 4: Commit and push if changes
    if ! git diff-index --quiet HEAD --; then
        echo "  Committing changes..."
        git add . && git commit -m "nightly: Backend improvements" && git push origin nightly-improvements 2>/dev/null && echo "  ✓ Pushed to nightly-improvements"
    else
        echo "  ✓ No changes to commit"
    fi
}

process_frontend() {
    echo ""
    echo "=== Processing Frontend (welcome-frontend) ==="
    cd "$WORKING_DIR/welcome-frontend"
    
    # Check branch
    local current_branch=$(git branch --show-current)
    echo "Current branch: $current_branch"
    
    # Checkout nightly-improvements if on main
    if [[ "$current_branch" == "main" || "$current_branch" == "master" ]]; then
        git checkout nightly-improvements 2>/dev/null || {
            echo "Creating nightly-improvements branch..."
            git checkout -b nightly-improvements
        }
    fi
    
    # Pull latest
    git pull origin nightly-improvements 2>/dev/null || echo "No remote nightly-improvements branch"
    
    # Task 1: Cleanup temp files
    find . -name "*.tmp" -o -name "*.log" 2>/dev/null | xargs rm -rf 2>/dev/null
    echo "✓ Cleanup temp files"
    
    # Task 2: Check TODOs
    local todo_count=$(grep -r "TODO\|FIXME" frontend/src/ --include="*.jsx" --include="*.js" 2>/dev/null | wc -l)
    echo "  Frontend TODOs: $todo_count"
    
    # Task 3: Commit and push if changes
    if ! git diff-index --quiet HEAD --; then
        echo "  Committing changes..."
        git add . && git commit -m "nightly: Frontend improvements" && git push origin nightly-improvements 2>/dev/null && echo "  ✓ Pushed to nightly-improvements"
    else
        echo "  ✓ No changes to commit"
    fi
}

main "$@"
