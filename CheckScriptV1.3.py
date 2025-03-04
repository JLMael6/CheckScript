import os
import re
import argparse
from datetime import datetime
 
# ------------------------------
# CONSTANTES ET CONFIGURATION
# ------------------------------
FORBIDDEN_FOLDERS = {"Temp", "CleanBackUp", "DebuggerSave"}
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
LOGS_DIR = os.path.join(SCRIPT_DIR, "logs")
RESULTS_DIR = os.path.join(SCRIPT_DIR, "resultats")
LOG_FILE = os.path.join(LOGS_DIR, "Checks_Log.txt")
RESULTS_FILE = os.path.join(RESULTS_DIR, "Checks_Results.txt")
 
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
 
# Vider les fichiers log et résultat au démarrage
open(LOG_FILE, "w", encoding="utf-8").close()
open(RESULTS_FILE, "w", encoding="utf-8").close()
 
# ------------------------------
# FONCTIONS DE VÉRIFICATION
# ------------------------------
def normalize_path(path):
    """ Normalise le chemin pour être uniforme entre OS. """
    return os.path.normpath(path).replace('\\', '/').lower()
 
def check_forbidden_folders(root_dir, environment):
    """ Vérifie la présence de dossiers interdits dans les projets, sauf en DEV. """
    errors = []
    for dirpath, dirnames, _ in os.walk(root_dir):
        log_message(f"Analyse en cours de: {dirpath}", level="INFO")
        if environment != "DEV":
            for forbidden in FORBIDDEN_FOLDERS:
                if forbidden in dirnames:
                    forbidden_dir_path = os.path.join(dirpath, forbidden)
                    errors.append(f"Veuillez vérifier ce dossier {forbidden_dir_path}")
                    log_message(f"Veuillez vérifier ce dossier {forbidden_dir_path}", level="WARNING")
        else:
            log_message("Aucun test sur les dossiers interdits en DEV.", level="INFO")
    return errors
 
def check_license_in_ini(file_path, expected_license):
    """ Vérifie la licence dans le fichier ifs.ini et renvoie une erreur si elle est incorrecte. """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            content = file.read()  # Lire tout le fichier d'un coup
 
        # Recherche de la licence avec regex
        match = re.search(r"\[MAGIC_ENV\]LicenseName=(\S+)", content)
 
        if not match:
            return f"Erreur de licence dans {file_path}: Aucune licence trouvée, la licence attendue est '{expected_license}'."
 
        found_license = f"LicenseName={match.group(1)}"
 
        if found_license != expected_license:
            return f"Erreur de licence dans {file_path}: La licence trouvée est '{found_license}', mais la licence attendue est '{expected_license}'."
 
        return None  # Pas d'erreur, la licence est correcte
 
    except Exception as e:
        return f"Erreur lors de la lecture du fichier {file_path}: {e}"
 
def check_sql_file(file_path):
    """ Vérifie si un fichier SQL est dans le bon dossier. """
    if 'document/sql' not in normalize_path(file_path):
        return f"{file_path} n'est pas dans le dossier 'document/sql'"
    return None
 
def process_file(file_path, file_name, expected_license):
    """ Processus de vérification pour chaque fichier. """
    if file_name.lower() == 'ifs.ini':
        return check_license_in_ini(file_path, expected_license)
    elif file_name.lower().endswith('.sql'):
        return check_sql_file(file_path)
    return None
 
# ------------------------------
# ANALYSE PRINCIPALE
# ------------------------------
def run_checks(root_dir, expected_license, environment):
    """ Exécute toutes les vérifications. """
    log_message(f"Début des vérifications pour {root_dir}", level="INFO")
    errors = check_forbidden_folders(root_dir, environment)  # Vérification des dossiers interdits
    for dirpath, _, filenames in os.walk(root_dir):
        log_message(f"Analyse en cours de: {dirpath}", level="INFO")
        for file_name in filenames:
            file_path = os.path.join(dirpath, file_name)
            # Vérification du contenu du fichier
            file_error = process_file(file_path, file_name, expected_license)
            if file_error:
                errors.append(file_error)
                log_message(file_error, level="ERROR" if "Licence" in file_error else "WARNING")
 
    # Ajouter un message d'info si aucun dossier interdit n'a été trouvé
    if environment != "DEV" and not any(folder in error for folder in FORBIDDEN_FOLDERS for error in errors):
        info_message = "Aucun dossier interdit trouvé"
        log_message(info_message, level="INFO")
        errors.append(info_message)
 
    log_message("Analyse terminée", level="SUCCESS")
    return errors
 
# ------------------------------
# SAUVEGARDE DES RÉSULTATS
# ------------------------------
def save_results_to_file(results):
    """ Sauvegarde les erreurs dans un fichier résultat avec le niveau approprié. """
    try:
        with open(RESULTS_FILE, "w", encoding="utf-8", errors="ignore") as result_file:
            timestamp = datetime.now().strftime("%Y-%m-%d;%H:%M:%S.") + f"{datetime.now().microsecond // 1000:03d}"
            result_file.write(f"{timestamp};0;INFO;Résultats de l'analyse:\n")
            for error in results:
                result_level = "ERROR" if "La licence trouvée est" in error else "WARNING"
                result_file.write(f"{timestamp};0;{result_level};{error}\n")
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
    args = parser.parse_args()
    root_dir = args.folder
    license_map = {
        "PROD": "LicenseName=IBPRSRVI",
        "PREPROD": "LicenseName=IBPRSRVI",
        "DEV": "LicenseName=IBNPSRV"
    }
    results = run_checks(root_dir, license_map[args.environment], args.environment)
    save_results_to_file(results)