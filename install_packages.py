import argparse
import os
import subprocess
import sys
import time
import yaml

CACHE_UPDATE_INTERVAL = 7200  # Mettre à jour le cache des paquets toutes les 2 heures (en secondes)

def install_packages(packages):
    """
    Installe les packages spécifiés en utilisant la commande apt-get install.
    Les packages déjà installés sont affichés en vert avec leur numéro de version.
    Les packages à installer sont affichés en bleu.
    """

    # Initialise deux dictionnaires pour stocker les paquets déjà installés et les paquets à installer
    installed_packages = {}
    to_install_packages = []

    # Parcourt la liste des paquets et vérifie s'ils sont déjà installés
    for package in packages:
        result = subprocess.run(['dpkg', '-s', package], capture_output=True, text=True)
        if result.returncode == 0:
            # Si le paquet est déjà installé, stocke le numéro de version dans le dictionnaire installed_packages
            version = ''
            for line in result.stdout.split('\n'):
                if line.startswith('Version:'):
                    version = line.split()[1]
                    break
            installed_packages[package] = version
        else:
            # Si le paquet n'est pas installé, l'ajoute à la liste des paquets à installer
            to_install_packages.append(package)

    # Affiche les paquets déjà installés en vert avec leur numéro de version
    if installed_packages:
        print('Packages already installed:')
        for package, version in installed_packages.items():
            print(f'\033[92m{package} ({version})\033[0m')

    # Si des paquets doivent être installés, affiche-les en bleu et installe-les en utilisant apt-get install
    if to_install_packages:
        print('Packages to install:')
        for package in to_install_packages:
            print(f'\033[94m{package}\033[0m')
        command = ['apt-get', 'update', '-y']  # Met à jour le cache des paquets
        subprocess.run(command)
        command = ['apt-get', 'install', '-y'] + to_install_packages  # Installe les paquets à partir de la liste to_install_packages
        subprocess.run(command)
    else:
        # Si aucun paquet n'a besoin d'être installé, affiche un message approprié
        print('No new packages to install.')


def main():
    """
    Fonction principale du script. Analyse les arguments de la ligne de commande, charge le fichier YAML et installe les packages.
    """
    # Analyse des arguments de la ligne de commande
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', help='Path to the YAML file containing the packages to install', default='packages.yaml')
    parser.add_argument('-c', '--category', help='Name of the category to install')
    parser.add_argument('-s', '--subcategories', help='Name of the subcategories to install', nargs='*', default=[])
    args = parser.parse_args()

    # Vérifie si l'utilisateur est root
    if os.geteuid() != 0:
        print('This script must be run as root!')
        sys.exit(1)

    # Charge le fichier YAML
    with open(args.file) as f:
        data = yaml.load(f, Loader=yaml.FullLoader)

    # Vérifie si la catégorie est présente dans le fichier YAML
    if args.category not in data:
        print(f'Category "{args.category}" not found in the YAML file!')
        sys.exit(1)

    # Récupère la liste des packages à installer
    packages = []
    for subcategory in args.subcategories:
        if subcategory in data[args.category]:
            packages += data[args.category][subcategory]
    if 'other_packages' in data[args.category]:
        packages += data[args.category]['other_packages']

    # Supprime les doublons
    packages = list(set(packages))

    # Vérifie l'heure du dernier apt-get update
    dotfile_path = os.path.expanduser('~/.install_packages_last_update')
    if os.path.exists(dotfile_path):
        with open(dotfile_path, 'r') as f:
            last_update_time = int(f.read())
    else:
        last_update_time = 0

    current_time = time.time()
    if current_time - last_update_time > CACHE_UPDATE_INTERVAL:
        print('Updating package cache...')
        command = ['apt-get', 'update', '-y']
        subprocess.run(command)
        with open(dotfile_path, 'w') as f:
            f.write(str(int(current_time)))

    # Installe les packages
    install_packages(packages)

if __name__ == '__main__':
    main()
