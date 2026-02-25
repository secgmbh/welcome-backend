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
    
    # Change to working directory
    cd "$WORKING_DIR"
    
    # Switch to nightly-improvements branch
    git checkout nightly-improvements 2>/dev/null || {
        echo "Branch nightly-improvements not found, creating..."
        git checkout -b nightly-improvements
    }
    
    # Pull latest changes
    git pull origin nightly-improvements 2>/dev/null
    
    # Your nightly improvement tasks go here:
    echo "Running nightly checks..."
    
    # Task 1: Cleanup temporary files
    find "$WORKING_DIR" -name "*.tmp" -o -name "*.log" -o -name "*.pyc" 2>/dev/null | xargs rm -f 2>/dev/null
    echo "✓ Cleanup temporary files"
    
    # Task 2: Check for TODO comments
    echo "Checking TODO comments..."
    local todo_count=$(grep -r "TODO\|FIXME" "$WORKING_DIR" --include="*.py" --include="*.jsx" --include="*.js" 2>/dev/null | wc -l)
    echo "  Found $todo_count TODO comments"
    
    # Task 3: Check for print statements in Python (should use logger)
    echo "Checking for print() statements in Python..."
    local print_count=$(grep -r "^\s*print(" "$WORKING_DIR" --include="*.py" 2>/dev/null | wc -l)
    if [[ $print_count -gt 0 ]]; then
        echo "  ⚠️  Found $print_count print() statements (should use logger)"
    else
        echo "  ✓ No print() statements found"
    fi
    
    # Task 4: Check git status for uncommitted changes
    echo "Checking git status..."
    cd "$WORKING_DIR"
    if ! git diff-index --quiet HEAD -- 2>/dev/null; then
        echo "  ⚠️  Uncommitted changes detected"
    else
        echo "  ✓ No uncommitted changes"
    fi
    
    echo "Nightly improvements completed!"
}

main "$@"
