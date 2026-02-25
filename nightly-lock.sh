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
    
    # Example: Check for outdated dependencies, run tests, etc.
    
    echo "Nightly improvements completed!"
}

main "$@"
