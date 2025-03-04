import os
import re
import argparse
import xml.etree.ElementTree as ET
from datetime import datetime

# ------------------------------
# CONSTANTES ET CONFIGURATION
# ------------------------------
FORBIDDEN_FOLDERS = {"Temp", "CleanBackUp", "DebuggerSave", "files", "Flow124"}
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
LOGS_DIR = os.path.join(SCRIPT_DIR, "logs")
RESULTS_DIR = os.path.join(SCRIPT_DIR, "resultats")
LOG_FILE = os.path.join(LOGS_DIR, "Checks_Log.txt")
RESULTS_FILE = os.path.join(RESULTS_DIR, "Checks_Results.txt")
MAGIC_FOLDERS = {
    "DEV": "MagicDev",
    "PREPROD": "MagicPPrd",
    "PROD": "MagicPrd"
}

# Liste des adresses longues valides, séparées par environnement
VALID_SERVERS = {
    "DEV": [
        "wezjwcxpadwv002.pwcglb.com",
    ],
    "PREPROD": [
        "wezjwcxpapwv001.pwcglb.com",
        "wezjwcxpapwv002.pwcglb.com",
    ],
    "PROD": [
        "wezjwcxpapwv004.pwcglb.com",
        "wezjwcxpapwv005.pwcglb.com",
    ],
}

# ------------------------------
# LOGGING
# ------------------------------
def log_message(message, level="SUCCESS"):
    """ Écrit un message dans le fichier log et l'affiche à l'écran. """
    timestamp = datetime.now().strftime("%Y-%m-%d;%H:%M:%S.") + f"{datetime.now().microsecond // 1000:03d}"
    formatted_message = f"{timestamp};0;{level};{message}"
    try:
        with open(LOG_FILE, "a", encoding="utf-8", errors="ignore") as log:
            log.write(f"{formatted_message}\n")
        print(formatted_message)
    except Exception as e:
        print(f"Erreur lors de l'écriture dans le log : {e}")

# ------------------------------
# Dossiers et fichiers
# ------------------------------
def ensure_writable(path, is_directory=True):
    """ Vérifie qu'un fichier ou dossier est accessible en écriture et le crée si nécessaire. """
    if is_directory:
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
            log_message(f"Création du dossier: {path}", level="INFO")
        os.chmod(path, 0o777)
    else:
        if os.path.exists(path):
            os.chmod(path, 0o777)

ensure_writable(LOGS_DIR, is_directory=True)
ensure_writable(RESULTS_DIR, is_directory=True)
ensure_writable(LOG_FILE, is_directory=False)
ensure_writable(RESULTS_FILE, is_directory=False)

# Création/vidage des fichiers de logs et résultats au démarrage
open(LOG_FILE, "w", encoding="utf-8").close()
open(RESULTS_FILE, "w", encoding="utf-8").close()

# ------------------------------
# VÉRIFICATIONS
# ------------------------------
def check_forbidden_folders(root_dir, environment):
    """ Vérifie la présence de dossiers interdits dans les projets, sauf en DEV. """
    errors = []
    for dirpath, dirnames, _ in os.walk(root_dir):
        log_message(f"Scan du dossier : {dirpath}", level="INFO")
        if environment != "DEV":
            for forbidden in FORBIDDEN_FOLDERS:
                if forbidden in dirnames:
                    forbidden_dir_path = os.path.join(dirpath, forbidden)
                    errors.append(f"Veuillez vérifier ce dossier {forbidden_dir_path}")
                    log_message(f"Veuillez vérifier ce dossier {forbidden_dir_path}", level="WARNING")
    return errors

def check_license_in_ini(file_path, expected_license):
    """ Vérifie la licence dans le fichier ifs.ini et renvoie une erreur si elle est incorrecte. """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            content = file.read()
        match = re.search(r"\[MAGIC_ENV\]LicenseName=(\S+)", content)
        if not match:
            return f"Erreur de licence dans {file_path}: Aucune licence trouvée, attendue '{expected_license}'."
        found_license = f"LicenseName={match.group(1)}"
        if found_license != expected_license:
            return f"Erreur de licence dans {file_path}: trouvée '{found_license}', attendue '{expected_license}'."
        return None
    except Exception as e:
        return f"Erreur lors de la lecture du fichier {file_path}: {e}"

def check_version_file(root_dir):
    """ Vérifie la présence du fichier Version.txt dans les dossiers contenant DebuggerSave. """
    for dirpath, dirnames, _ in os.walk(root_dir):
        if "DebuggerSave" in dirnames:
            version_file = os.path.join(dirpath, "Version.txt")
            if not os.path.exists(version_file):
                log_message(f"Veuillez ajouter ce fichier manquant: {version_file}", level="ERROR")
                return [f"Veuillez ajouter ce fichier manquant: {version_file}"]
            return []  
    return []  

def check_suo_file(file_path, root_dir, environment):
    """ Vérifie les fichiers .suo en PROD ou PREPROD. """
    if environment in ["PREPROD", "PROD"] and file_path.lower().endswith(".suo"):
        relative_path = os.path.relpath(file_path, root_dir)
        if len(relative_path.split(os.sep)) == 2:
            log_message(f"Veuillez supprimer ce fichier en {environment}: {file_path}", level="ERROR")
            return f"Veuillez supprimer ce fichier en {environment}: {file_path}"
    return None

def check_start_xml(file_path, environment):
    """ Vérifie le fichier start.xml et sa cohérence d'environnement et les adresses des serveurs. """
    erreurs = []
    env_mapping = {"DEV": "MagicDev", "PREPROD": "MagicPPrd", "PROD": "MagicPrd"}
    expected_magic_env = env_mapping.get(environment, "")
    valid_servers = VALID_SERVERS.get(environment, [])

    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        project_element = root.find(".//Project")

        if project_element is not None:
            projects_dir = project_element.get("ProjectsDirPath", "")
            detected_env = None

            for key, value in env_mapping.items():
                if value in projects_dir:
                    detected_env = value
                    break

            if detected_env and detected_env != expected_magic_env:
                corrected_path = projects_dir.replace(detected_env, expected_magic_env)
                erreur_message = (f"Incohérence dans {file_path}: Environnement détecté '{detected_env}', "
                                  f"mais attendu '{expected_magic_env}'. "
                                  f"Veuillez corriger en : ProjectsDirPath='{corrected_path}'")
                erreurs.append(erreur_message)
                log_message(erreur_message, level="WARNING")

            # Vérification des adresses serveurs
            server_element = root.find(".//Server")
            if server_element is not None:
                host = server_element.get("host")
                alternate_hosts = server_element.get("alternateHosts", "")

                # Vérifier que l'adresse du serveur est valide
                if host not in valid_servers:
                    erreur_message = (f"Adresse serveur invalide dans {file_path}: {host}. "
                                      f"L'adresse détectée dans start.xml est '{host}', "
                                      f"et l'adresse attendue doit être une des adresses suivantes : "
                                      f"{', '.join(valid_servers)}")
                    erreurs.append(erreur_message)
                    log_message(erreur_message, level="ERROR")

                # Vérification des alternateHosts uniquement si l'environnement n'est pas DEV ou si alternateHosts est non vide
                if environment != "DEV" or alternate_hosts:
                    for alternate_host in alternate_hosts.split(","):
                        if alternate_host not in valid_servers:
                            erreur_message = (f"Adresse alternateHosts invalide dans {file_path}: {alternate_host}. "
                                              f"L'adresse détectée dans start.xml est '{alternate_host}', "
                                              f"et l'adresse attendue doit être une des adresses suivantes : "
                                              f"{', '.join(valid_servers)}")
                            erreurs.append(erreur_message)
                            log_message(erreur_message, level="ERROR")

    except Exception as e:
        erreurs.append(f"Erreur de lecture du fichier XML {file_path}: {e}")
        log_message(erreurs[-1], level="ERROR")

    return erreurs

def process_file(file_path, file_name, expected_license, root_dir, environment):
    """ Processus de vérification pour chaque fichier. """
    errors = []
    
    # Si le fichier est dans un dossier interdit, on l'ignore
    if any(forbidden in file_path for forbidden in FORBIDDEN_FOLDERS):
        log_message(f"Fichier ignoré car dans un dossier interdit: {file_path}", level="INFO")
        return errors

    # Vérification uniquement si le fichier ifs.ini est à la racine du dossier (pas dans un sous-dossier comme Temp)
    if file_name.lower() == 'ifs.ini' and os.path.dirname(file_path) == root_dir:
        license_error = check_license_in_ini(file_path, expected_license)
        if license_error:
            errors.append(license_error)
    elif file_name.lower().endswith('.suo'):
        suo_error = check_suo_file(file_path, root_dir, environment)
        if suo_error:
            errors.append(suo_error)
    elif file_name.lower() == "start.xml":
        errors.extend(check_start_xml(file_path, environment))
    return errors

def check_projects(root_dir, environment):
    """ Vérifie la présence des projets dans les dossiers Projects des environnements MagicDev, MagicPrd et MagicPPrd. """
    errors = []
    prod_projects = set()
    preprod_projects = set()
    dev_projects = set()

    # Vérification des projets dans les environnements spécifiés
    for env_key, env_value in MAGIC_FOLDERS.items():
        magic_dir = os.path.join(root_dir, env_value, "Projects")
        if os.path.exists(magic_dir):
            log_message(f"Scan du dossier {magic_dir}", level="INFO")
            for dirpath, dirnames, _ in os.walk(magic_dir):
                for dir_name in dirnames:
                    # Ignorer les éléments qui ne sont pas des projets
                    if dir_name not in {"Temp", "CleanBackUp", "DebuggerSave", "files", "Flow124"} and dir_name.startswith("PWC_"):
                        # Ajout du projet uniquement s'il commence par PWC_
                        if env_key == "PROD":
                            prod_projects.add(dir_name)
                        elif env_key == "PREPROD":
                            preprod_projects.add(dir_name)
                        elif env_key == "DEV":
                            dev_projects.add(dir_name)

        else:
            log_message(f"Le dossier 'Projects' est manquant dans {magic_dir}.", level="ERROR")
            errors.append(f"Le dossier 'Projects' est manquant dans {magic_dir}.")

    # Affichage des projets trouvés en PROD, PREPROD et DEV
    log_message(f"Projets trouvés en PROD: {', '.join(prod_projects)}", level="INFO")
    log_message(f"Projets trouvés en PREPROD: {', '.join(preprod_projects)}", level="INFO")
    log_message(f"Projets trouvés en DEV: {', '.join(dev_projects)}", level="INFO")

    # Vérification que les projets en PROD sont également présents en DEV et PREPROD
    missing_in_preprod = prod_projects - preprod_projects
    missing_in_dev = prod_projects - dev_projects

    if environment == "PREPROD":
        if missing_in_dev:
            errors.append(f"Projets en PrePROD manquants en DEV: {', '.join(missing_in_dev)}")
            log_message(f"Projets en PrePROD manquants en DEV: {', '.join(missing_in_dev)}", level="WARNING")
    else:
        if missing_in_preprod:
            errors.append(f"Projets en PROD manquants en PREPROD: {', '.join(missing_in_preprod)}")
            log_message(f"Projets en PROD manquants en PREPROD: {', '.join(missing_in_preprod)}", level="WARNING")
        
        if missing_in_dev:
            errors.append(f"Projets en PROD manquants en DEV: {', '.join(missing_in_dev)}")
            log_message(f"Projets en PROD manquants en DEV: {', '.join(missing_in_dev)}", level="WARNING")

    return errors

# ------------------------------
# SAUVEGARDE DES RÉSULTATS
# ------------------------------
def save_results_to_file(results):
    """ Sauvegarde les résultats dans un fichier. """
    try:
        with open(RESULTS_FILE, "w", encoding="utf-8", errors="ignore") as result_file:
            timestamp = datetime.now().strftime("%Y-%m-%d;%H:%M:%S.") + f"{datetime.now().microsecond // 1000:03d}"
            result_file.write(f"{timestamp};0;INFO;Résultats de l'analyse:\n")
            for error in results:
                result_file.write(f"{timestamp};0;WARNING;{error}\n")
        log_message(f"Résultats sauvegardés dans {RESULTS_FILE}", level="SUCCESS")
    except Exception as e:
        log_message(f"Erreur lors de la sauvegarde des résultats : {e}", level="WARNING")

# ------------------------------
# POINT D'ENTRÉE PRINCIPAL
# ------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Vérification des fichiers d'un projet.")
    parser.add_argument("environment", choices=["PROD", "PREPROD", "DEV"], help="Environnement à analyser.")
    parser.add_argument("--folder", help="Chemin du dossier à analyser.", required=True)
    parser.add_argument("--check-projects", action="store_true", help="Vérifier si les projets PROD sont présents en DEV et PREPROD.")
    args = parser.parse_args()

    if args.check_projects:
        # Vérification des projets dans les environnements
        errors = check_projects(args.folder, args.environment)
        if errors:
            save_results_to_file(errors)
        else:
            log_message("Aucune erreur trouvée concernant les projets.", level="SUCCESS")
    else:
        # Autres vérifications normales
        license_map = {
            "PROD": "LicenseName=IBPRSRVI",
            "PREPROD": "LicenseName=IBPRSRVI",
            "DEV": "LicenseName=IBNPSRV"
        }
        expected_license = license_map.get(args.environment)
        
        errors = check_forbidden_folders(args.folder, args.environment)
        errors.extend(check_version_file(args.folder))

        for dirpath, _, filenames in os.walk(args.folder):
            log_message(f"Scan du dossier : {dirpath}", level="INFO")
            for file_name in filenames:
                file_path = os.path.join(dirpath, file_name)
                file_errors = process_file(file_path, file_name, expected_license, args.folder, args.environment)
                errors.extend(file_errors)

        if errors:
            save_results_to_file(errors)
        else:
            log_message("Aucune erreur trouvée.", level="SUCCESS")