#  SSH Log Heuristic Analyzer & Blocker

Ce script Python agit comme un IPS (Intrusion Prevention System) léger, à l'image de Fail2Ban. Il analyse les fichiers de journaux d'authentification Linux (`auth.log`) pour identifier les schémas d'attaques par force brute sur le service SSH, et utilise `iptables` pour bloquer les adresses IP malveillantes.

##  Fonctionnalités
- Extraction par Regex (Expressions Régulières) des adresses IP malveillantes.
- Agrégation et gestion de seuils de tolérance (ex: blocage après 3 échecs).
- Bannissement automatisé via l'API `subprocess` et le pare-feu `iptables`.
- Mode "Simulation" inclus pour tester la détection sans altérer les règles de votre pare-feu.

##  Installation et Test local
Ce script utilise uniquement la bibliothèque standard de Python. Aucun paquet externe n'est requis.

Un fichier `sample_auth.log` est fourni dans ce dépôt pour vous permettre de tester le script immédiatement et sans danger.

```bash
git clone [https://github.com/FilouCosmos/ssh-log-analyzer.git](https://github.com/FilouCosmos/ssh-log-analyzer.git)
cd ssh-log-analyzer
python3 analyze_ssh.py
```

## Passage en Production
Pour utiliser ce script sur un vrai serveur Linux :

Éditez le fichier analyze_ssh.py.

Modifiez la variable CHEMIN_LOG_SSH pour pointer vers /var/log/auth.log (Debian/Ubuntu) ou /var/log/secure (RHEL/CentOS).

Passez la variable MODE_SIMULATION à False.

## Déploiement et Automatisation (Cron)
Pour que ce script agisse comme un véritable outil de sécurité actif, il doit tourner en permanence. Éditez la crontab de l'utilisateur root (sudo crontab -e) et ajoutez cette ligne pour exécuter l'analyseur toutes les 5 minutes :

```bash
*/5 * * * * /usr/bin/python3 /chemin/vers/ssh-log-analyzer/analyze_ssh.py >> /var/log/custom_fail2ban.log 2>&1
```

## Astuce SysAdmin : 
Pensez à configurer logrotate pour le fichier /var/log/custom_fail2ban.log afin d'éviter qu'il ne sature votre espace disque au fil des mois !
