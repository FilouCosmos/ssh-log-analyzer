import re
import os
from collections import Counter

# --- Config ---
LOG_FILE = "sample_auth.log" # /var/log/auth.log en prod
MAX_FAILURES = 3
DRY_RUN = True # Passer a False pour bloquer reellement
# ---------------------

def get_bad_ips(logfile):
    # Cherche le pattern "Failed password" et chope l'IP
    regex = re.compile(r"Failed password.*from\s+([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)")
    ips = []
    
    try:
        with open(logfile, 'r') as f:
            for line in f:
                match = regex.search(line)
                if match:
                    ips.append(match.group(1))
        return ips
    except Exception as e:
        print(f"[ERROR] Impossible de lire {logfile}: {e}")
        return []

def ban_ip(ip):
    cmd = f"iptables -A INPUT -s {ip} -j DROP"
    if DRY_RUN:
        print(f"[DRY-RUN] Exec: {cmd}")
    else:
        os.system(cmd)
        print(f"[ACTION] IP {ip} bannie du serveur.")

if __name__ == "__main__":
    print(f"[INFO] Analyse de {LOG_FILE}...")
    
    failed_ips = get_bad_ips(LOG_FILE)
    
    if failed_ips:
        # Compte le nb d'occurrences pour chaque IP
        ip_counts = Counter(failed_ips)
        
        for ip, count in ip_counts.items():
            if count >= MAX_FAILURES:
                print(f"[WARN] Bruteforce depuis {ip} ({count} echecs)")
                ban_ip(ip)
            else:
                print(f"[OK] {ip} : {count} echec(s) - ignore")
    else:
        print("[OK] Aucun echec suspect trouve dans les logs.")