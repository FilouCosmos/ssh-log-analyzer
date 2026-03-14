import re
import subprocess
from collections import Counter
from typing import Dict, List

# --- Configuration ---
# Pour tester sur GitHub, on utilise le fichier fourni.
# !!! EN PRODUCTION : Remplacez par "/var/log/auth.log" (ou /var/log/secure sur CentOS)
CHEMIN_LOG_SSH = "sample_auth.log" 
SEUIL_ECHECS = 3

# Mettre à False pour exécuter réellement la commande iptables (nécessite sudo)
MODE_SIMULATION = True 
# ---------------------

def extraire_ips_suspectes(chemin_fichier: str) -> List[str]:
    """Parcourt le fichier de log et extrait les IPs ayant échoué à s'authentifier."""
    pattern_echec = re.compile(r"Failed password.*from\s+([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)")
    ips = []
    
    try:
        with open(chemin_fichier, 'r') as f:
            for ligne in f:
                match = pattern_echec.search(ligne)
                if match:
                    ips.append(match.group(1))
    except FileNotFoundError:
        print(f"! Erreur : Impossible de trouver le fichier {chemin_fichier}")
    except PermissionError:
        print(f"! Erreur : Droits insuffisants pour lire {chemin_fichier}. Lancez avec sudo.")
        
    return ips

def bannir_ip(ip: str) -> None:
    """Bloque une adresse IP en utilisant le pare-feu iptables."""
    commande = ["iptables", "-A", "INPUT", "-s", ip, "-j", "DROP"]
    
    if MODE_SIMULATION:
        print(f"  [SIMULATION] Commande qui serait exécutée : {' '.join(commande)}")
    else:
        try:
            subprocess.run(commande, check=True)
            print(f" L'IP {ip} a été bannie avec succès via iptables.")
        except subprocess.CalledProcessError as e:
            print(f"! Erreur lors du bannissement de l'IP {ip} : {e}")
        except FileNotFoundError:
             print("! Erreur : La commande 'iptables' n'est pas installée sur ce système.")

if __name__ == "__main__":
    print(f" Analyse du fichier {CHEMIN_LOG_SSH} en cours...\n")
    liste_ips_echouees = extraire_ips_suspectes(CHEMIN_LOG_SSH)
    
    if liste_ips_echouees:
        compteur_ips: Dict[str, int] = dict(Counter(liste_ips_echouees))
        
        print(" Résultats de l'analyse :")
        for ip, tentatives in compteur_ips.items():
            if tentatives >= SEUIL_ECHECS:
                print(f"!!!  [ALERTE] Attaque par force brute détectée depuis {ip} ({tentatives} échecs).")
                bannir_ip(ip)
            else:
                print(f" {ip} : {tentatives} échec(s) - Toléré (sous le seuil).")
    else:
        print(" Aucun échec de connexion suspect détecté.")