#!/bin/bash
set -e

# CVE.ICU Docker Entrypoint
# Handles initial data sync and scheduled updates

LOG_FILE="/var/log/cveicu/build.log"
LOCK_FILE="/tmp/cveicu-build.lock"
LAST_BUILD_FILE="/app/data/cache/.last_build"

# Color codes for logging
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    local level=$1
    shift
    local message="$@"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    case $level in
        INFO)  color=$GREEN ;;
        WARN)  color=$YELLOW ;;
        ERROR) color=$RED ;;
        *)     color=$BLUE ;;
    esac
    
    echo -e "${color}[$timestamp] [$level] $message${NC}" | tee -a "$LOG_FILE"
}

# Check if a build is already running
check_lock() {
    if [ -f "$LOCK_FILE" ]; then
        pid=$(cat "$LOCK_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            log WARN "Build already running (PID: $pid), skipping..."
            return 1
        else
            log INFO "Stale lock file found, removing..."
            rm -f "$LOCK_FILE"
        fi
    fi
    return 0
}

# Create lock file
create_lock() {
    echo $$ > "$LOCK_FILE"
}

# Remove lock file
remove_lock() {
    rm -f "$LOCK_FILE"
}

# Check if we need to run a build (based on time since last build)
needs_build() {
    if [ ! -f "$LAST_BUILD_FILE" ]; then
        log INFO "No previous build found, build needed"
        return 0
    fi
    
    last_build=$(cat "$LAST_BUILD_FILE")
    current_time=$(date +%s)
    time_diff=$((current_time - last_build))
    
    # If more than UPDATE_INTERVAL seconds since last build, we need to build
    if [ "$time_diff" -gt "${UPDATE_INTERVAL:-3600}" ]; then
        log INFO "Last build was $((time_diff / 60)) minutes ago, build needed"
        return 0
    else
        log INFO "Last build was $((time_diff / 60)) minutes ago, within interval"
        return 1
    fi
}

# Run the build process
run_build() {
    local build_type="${1:-full}"
    
    if ! check_lock; then
        return 1
    fi
    
    create_lock
    trap remove_lock EXIT
    
    log INFO "=========================================="
    log INFO "Starting CVE.ICU $build_type build..."
    log INFO "=========================================="
    
    cd /app
    
    case $build_type in
        full)
            log INFO "Running full build (data download + processing)"
            python build.py 2>&1 | tee -a "$LOG_FILE"
            ;;
        quick)
            log INFO "Running quick build (templates only)"
            python data/scripts/quick_build.py 2>&1 | tee -a "$LOG_FILE"
            ;;
        *)
            log ERROR "Unknown build type: $build_type"
            return 1
            ;;
    esac
    
    build_status=$?
    
    if [ $build_status -eq 0 ]; then
        # Record successful build time
        date +%s > "$LAST_BUILD_FILE"
        log INFO "Build completed successfully"
        
        # Log some stats
        if [ -d "/app/web/data" ]; then
            json_count=$(find /app/web/data -name "*.json" 2>/dev/null | wc -l)
            log INFO "Generated $json_count JSON data files"
        fi
        if [ -d "/app/web" ]; then
            html_count=$(find /app/web -maxdepth 1 -name "*.html" 2>/dev/null | wc -l)
            log INFO "Generated $html_count HTML pages"
        fi
    else
        log ERROR "Build failed with status $build_status"
    fi
    
    remove_lock
    trap - EXIT
    
    return $build_status
}

# Scheduled update function (called by cron/supervisor)
scheduled_update() {
    log INFO "Scheduled update triggered"
    
    if needs_build; then
        run_build full
    else
        log INFO "Skipping scheduled build (within update interval)"
    fi
}

# Initial startup build
startup_build() {
    log INFO "=========================================="
    log INFO "CVE.ICU Container Starting"
    log INFO "=========================================="
    log INFO "Update Interval: ${UPDATE_INTERVAL:-3600} seconds"
    log INFO "Web Server Port: ${WEB_PORT:-8090}"
    log INFO "Timezone: ${TZ:-UTC}"
    log INFO "=========================================="
    
    # Check if we need to catch up (container was interrupted)
    if needs_build; then
        log INFO "Data is stale or missing, running startup build..."
        run_build full
    else
        log INFO "Data is fresh, skipping startup build"
        
        # Still regenerate templates in case code changed
        log INFO "Regenerating templates..."
        run_build quick
    fi
}

# Export functions for use in scheduled tasks
export -f log
export -f check_lock
export -f create_lock
export -f remove_lock
export -f needs_build
export -f run_build
export -f scheduled_update

# Main entry point
case "${1:-}" in
    build)
        # Manual build command
        run_build "${2:-full}"
        ;;
    update)
        # Scheduled update
        scheduled_update
        ;;
    serve)
        # Just serve (no build)
        cd /app/web
        exec python -m http.server ${WEB_PORT:-8090}
        ;;
    shell|bash)
        # Interactive shell
        exec /bin/bash
        ;;
    supervisord)
        # Normal startup with supervisor
        startup_build
        exec "$@"
        ;;
    *)
        # Default: startup build + supervisor
        startup_build
        exec supervisord -c /etc/supervisor/conf.d/supervisord.conf
        ;;
esac

