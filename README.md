# CheckScript

V1.0.0; Livraison Optimal
V1.0.1; Optimisation / Nouveaux Logs et résultats (30/01/2025)
V1.1; Ajout des dossiers CleanBackUp et DebuggerSave au dossier à vérifier.
V1.2; Normalisation des logs et Ajout d'un script powershell permettant une execution hebdomadaire (Task Scheduler).
V1.3; - Test de la présence de DebuggerSave,Temp et CleanBackUp uniquement sur l'environnement de PROD et PREPROD.
- Normalisation des logs et résultats par le changement de la severité d'erreur en ERROR lorsqu'une chaine de caractere n'est pas la bonne.
- Ajout d'une ligne lorsque aucun dossiers n'est à signaler.
- Optimisation du Script.
V1.4; Ajout d'un message indiquant qu'un fichier .suo est présent sur l'environnement de Preprod ou de Prod et qu'il faut le supprimer.
Vérification si un fichier version.txt est présent.
vérification dans le fichier start.xml du ProjectDirPath pour savoir si le bon environnement à été saisie et du serveur hôte.
V1.4.1; meilleur Optimisation de la V1.4
V1.5; Ajout de la fonction --Check-projects : permet la vérification de la présence des projets dans l'environnement de PROD dans les environnements de PREPROD et DEV, Idem en PREPROD pour verifier si les projets sont présents en DEV.
Correction de la vérification des fichiers ifs.ini, seul les fichiers à la racine des projets sont vérifiers.
Ajout d'une vérification dans le start.xml, il vérifie <Server host="" alternateHosts=""> et si ce n'est pas l'adresse de serveur long un message sera affiché et donnera la bonne adresse de serveur à mettre.
