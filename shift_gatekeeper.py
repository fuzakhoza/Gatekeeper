import os
import sys
import datetime
import subprocess
import logging
import pwd

def user_exists(username):
    """Checks if a user account exists on the system before modifying it."""
    try:
        pwd.getpwnam(username)
        return True
    except KeyError:
        return False


# 1. Enforce Root Privilege Check
if os.geteuid() != 0:
    print("[X] ACCESS DENIED: Gatekeeper requires root privileges. Run with 'sudo python3 shift_gatekeeper.py'")
    sys.exit(1)

LOG_FILE = '/var/log/gatekeeper.log'

# 2. Configure Audit Logging & Enforce Log Integrity (chmod 600)
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - [GATEKEEPER-v3] - %(levelname)s - %(message)s'
)
if os.path.exists(LOG_FILE):
    os.chmod(LOG_FILE, 0o600)

# Shift Schedule Configuration (Monday = 0 ... Sunday = 6)
OPEN_HOUR = 8
CLOSE_HOUR = 17
WORK_DAYS = [0, 1, 2, 3, 4]  # Monday to Friday only

# Target Assets (NEVER include root or break-glass admin accounts)
STAFF_USERS = ["test_clerk"]
RESTRICTED_PORTS = ["22/tcp"]

def broadcast_warning(message):
    """Sends a system-wide terminal alert to logged-in users to protect data integrity."""
    subprocess.run(["wall", message], check=False)
    logging.info(f"BROADCAST SENT: {message}")

def is_user_logged_in(username):
    """Checks if a target user currently has an active terminal session."""
    result = subprocess.run(["pgrep", "-u", username], stdout=subprocess.DEVNULL)
    return result.returncode == 0

def enforce_cia_perimeter():
    now = datetime.datetime.now()
    current_day = now.weekday()
    current_hour = now.hour
    current_minute = now.minute

    is_workday = current_day in WORK_DAYS
    is_working_hours = OPEN_HOUR <= current_hour < CLOSE_HOUR

    # INTEGRITY CHECK: 5-Minute Graceful Warning at 16:55 on Workdays
    if is_workday and current_hour == (CLOSE_HOUR - 1) and current_minute == 55:
        broadcast_warning("⚠️ [GATEKEEPER ALERT]: Shift ends in 5 minutes (17:00). Save all work now before automated session termination.")
        return

    # AVAILABILITY & CONFIDENTIALITY: Open Doors During Valid Shift Hours
    if is_workday and is_working_hours:
        for user in STAFF_USERS:
            subprocess.run(["usermod", "-U", user], check=False)
        for port in RESTRICTED_PORTS:
            subprocess.run(["ufw", "allow", port], stdout=subprocess.DEVNULL, check=False)
        
        # Log state transitions cleanly at the start of the shift (08:00)
        if current_hour == OPEN_HOUR and current_minute == 0:
            logging.info("SHIFT OPEN (08:00): Staff accounts unlocked and authorized ports opened.")
            print("[✓] SHIFT OPEN: Doors unlocked.")

    # CONFIDENTIALITY & INTEGRITY: Lock Doors After Hours & All Weekend
    else:
        for user in STAFF_USERS:
            if is_user_logged_in(user):
                # Use SIGTERM (-15) first to allow clean application closure without corrupting files
                subprocess.run(["pkill", "-TERM", "-u", user], check=False)
                logging.warning(f"Graceful SIGTERM sent to active session: {user}")
            subprocess.run(["usermod", "-L", user], check=False)

        for port in RESTRICTED_PORTS:
            subprocess.run(["ufw", "delete", "allow", port], stdout=subprocess.DEVNULL, check=False)

        if current_hour == CLOSE_HOUR and current_minute == 0:
            logging.warning("SHIFT CLOSED (17:00): Doors bolted, accounts locked, and ports sealed.")
            print("[!] SHIFT CLOSED: Perimeter sealed.")

if __name__ == "__main__":
    enforce_cia_perimeter()
