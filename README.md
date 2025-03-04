
# CheckScript

## Description (Français)

Ce script est conçu pour vérifier l’intégrité et la conformité des fichiers dans un projet en fonction de l’environnement spécifié (PROD, PREPROD, DEV). Il s’assure que les dossiers et fichiers respectent certaines règles et attentes, notamment :

1. Vérification des dossiers interdits.
2. Validation des informations de licence dans le fichier `ifs.ini`.
3. Vérification de la présence des fichiers nécessaires, tels que `Version.txt`.
4. Vérification des fichiers `.suo` en fonction de l’environnement.
5. Vérification du fichier `start.xml` pour garantir que les chemins de projets et les adresses des serveurs sont corrects.
6. Validation de la présence des projets dans les environnements appropriés (DEV, PREPROD, PROD).

Les erreurs détectées sont enregistrées dans un fichier de log et un fichier de résultats.

### Fonctionnalités

- **Vérification des dossiers interdits** : Le script recherche certains dossiers interdits dans les répertoires du projet, sauf en environnement DEV.
- **Validation des licences** : Le script vérifie la licence dans le fichier `ifs.ini` et s’assure qu’elle correspond à la licence attendue selon l’environnement.
- **Fichier Version.txt** : Le script vérifie que le fichier `Version.txt` est présent dans les dossiers nécessaires.
- **Fichiers `.suo`** : En environnement PREPROD et PROD, il vérifie que les fichiers `.suo` ne sont pas présents dans des répertoires non valides.
- **Fichier `start.xml`** : Le script vérifie l’existence et la validité du fichier `start.xml`, notamment la cohérence des chemins de projets et des serveurs.
- **Projets dans les environnements** : Le script s’assure que les projets présents en PROD sont également présents en DEV et PREPROD.

### Prérequis

- Python 3.x
- Accès en lecture/écriture aux dossiers et fichiers du projet.

## Installation

Clonez ce repository sur votre machine locale :

```bash
git clone https://github.com/JLMael6/CheckScript
```

## Utilisation

Exécutez le script en ligne de commande en spécifiant l’environnement et le chemin du dossier à analyser :

```bash
python check_project.py <ENVIRONNEMENT> --folder <CHEMIN_DU_DOSSIER>
```

### Paramètres

- `environment` : L’environnement à analyser. Les valeurs possibles sont `PROD`, `PREPROD`, ou `DEV`.
- `--folder` : Le chemin vers le dossier contenant les projets à analyser.
- `--check-projects` : Option facultative. Vérifie que les projets PROD sont présents en DEV et PREPROD.

### Exemple

```bash
python check_project.py PROD --folder /chemin/vers/projet --check-projects
```

## Résultats

Les résultats des vérifications sont enregistrés dans deux fichiers :

- **Logs** : Un fichier `Checks_Log.txt` dans le dossier `logs` qui enregistre tous les événements importants.
- **Résultats** : Un fichier `Checks_Results.txt` dans le dossier `resultats` qui liste les erreurs ou incohérences détectées.

## Licence

Ce script est distribué sous la licence MIT.

---

## Description (English)

This script is designed to check the integrity and compliance of files in a project based on the specified environment (PROD, PREPROD, DEV). It ensures that the folders and files adhere to certain rules and expectations, including:

1. Checking for forbidden folders.
2. Validating license information in the `ifs.ini` file.
3. Checking for the presence of required files, such as `Version.txt`.
4. Validating `.suo` files depending on the environment.
5. Checking the `start.xml` file to ensure project paths and server addresses are correct.
6. Ensuring the presence of projects in the appropriate environments (DEV, PREPROD, PROD).

Any detected errors are logged and saved in a results file.

### Features

- **Forbidden Folders Check**: The script searches for specific forbidden folders in project directories, except in the DEV environment.
- **License Validation**: The script checks the license in the `ifs.ini` file and ensures it matches the expected license for the environment.
- **Version.txt File**: The script checks that the `Version.txt` file is present in the necessary directories.
- **.suo Files**: In PREPROD and PROD environments, it checks that `.suo` files are not present in invalid directories.
- **start.xml File**: The script checks the existence and validity of the `start.xml` file, especially the consistency of project paths and server addresses.
- **Projects in Environments**: The script ensures that projects present in PROD are also present in DEV and PREPROD.

### Requirements

- Python 3.x
- Read/Write access to the project’s folders and files.

## Installation

Clone this repository to your local machine:

```bash
git clone https://github.com/JLMael6/CheckScript
```

## Usage

Run the script from the command line, specifying the environment and the folder to analyze:

```bash
python check_project.py <ENVIRONMENT> --folder <FOLDER_PATH>
```

### Parameters

- `environment` : The environment to analyze. Possible values are `PROD`, `PREPROD`, or `DEV`.
- `--folder` : The path to the folder containing the projects to analyze.
- `--check-projects` : Optional. Checks that PROD projects are present in DEV and PREPROD.

### Example

```bash
python check_project.py PROD --folder /path/to/project --check-projects
```

## Results

The verification results are saved in two files:

- **Logs**: A `Checks_Log.txt` file in the `logs` folder that logs all important events.
- **Results**: A `Checks_Results.txt` file in the `results` folder that lists any errors or inconsistencies found.

## License

This script is distributed under the MIT license.
