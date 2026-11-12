# 🛡️ Gatekeeper v3: CIA-Aligned Time-Based Access Control & Perimeter Hardening

**Gatekeeper** is an automated, zero-dependency Python security daemon engineered to enforce strict **Time-Based Access Control (TBAC)**, dynamic firewall port sealing, and tamper-evident audit logging on Linux workstations and enterprise servers.

## 🔐 Built on the CIA Triad

| CIA Pillar | Security Control Implemented | Operational Impact |
| :--- | :--- | :--- |
| **Confidentiality** | Locks staff accounts (`usermod -L`), seals SSH ports (`ufw`), and enforces full weekend lockdowns (`Sat–Sun`). | Eliminates overnight and weekend attack surfaces against brute-force bots and unauthorized after-hours access. |
| **Integrity** | Broadcasts a 5-minute `wall` warning at `16:55`, uses graceful `SIGTERM` (`pkill -TERM`) at `17:00`, and locks audit logs to `chmod 600` (`root` only). | Prevents open database or file corruption during session termination and protects audit logs from tampering. |
| **Availability** | Excludes dedicated break-glass admin accounts from lockdown and executes every 60 seconds via `cron`. | Ensures zero-minute delays at `08:00` shift start and uninterrupted emergency admin access 24/7. |

## ⚙️ Operational Timeline (Monday – Friday)
* **08:00:** Unlocks authorized staff accounts, opens configured remote management ports (`22/tcp`), and logs `SHIFT OPEN` telemetry.
* **16:55:** Broadcasts a system-wide terminal alert warning active users to save open files before automated closure.
* **17:00:** Sends graceful `SIGTERM` to active staff sessions, bolts user accounts (`L` status), seals remote firewall ports, and logs `SHIFT CLOSED` telemetry.
* **Saturday & Sunday:** Enforces continuous 48-hour weekend perimeter lockdown.

## 🚀 Deployment Instructions

1. **Configure Target Accounts & Ports:**
   Edit `STAFF_USERS` and `RESTRICTED_PORTS` inside `shift_gatekeeper.py` (never add `root` or emergency administrator accounts).

2. **Verify Root Privilege Enforcement:**
   ```bash
   sudo python3 shift_gatekeeper.py
   ```

3. **Schedule 1-Minute Automated Execution (`cron`):**
   ```bash
   sudo crontab -e
   # Add the following line at the bottom:
   * * * * * /usr/bin/python3 /path/to/shift_gatekeeper.py
   ```

## 🔍 Sample SIEM-Ready Audit Telemetry (`/var/log/gatekeeper.log`)
```text
2026-11-12 13:13:44,781 - [GATEKEEPER] - INFO - SHOP OPEN (13:13): Unlocking staff accounts and opening authorized ports.
2026-11-12 13:13:44,809 - [GATEKEEPER] - INFO - Account UNLOCKED: test_clerk
2026-11-12 13:13:45,227 - [GATEKEEPER] - INFO - Firewall port OPENED: 22/tcp
2026-11-12 13:25:03,709 - [GATEKEEPER] - WARNING - SHOP CLOSED (13:25): Terminating sessions, locking doors, and sealing ports.
2026-11-12 13:25:03,750 - [GATEKEEPER] - WARNING - Session KILLED & Account LOCKED: test_clerk
2026-11-12 13:25:04,087 - [GATEKEEPER] - WARNING - Firewall port SEALED: 22/tcp
```
