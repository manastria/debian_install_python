#!/usr/bin/env python3


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


def parse_arguments():
    """
    Parse les arguments de la ligne de commande et les retourne sous forme d'un objet argparse.Namespace.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', help='Path to the YAML file containing the packages to install', default='packages.yaml')
    parser.add_argument('-c', '--category', help='Name of the category to install')
    parser.add_argument('-s', '--subcategories', help='Name of the subcategories to install', nargs='*', default=[])
    return parser.parse_args()

def check_root():
    """
    Vérifie si l'utilisateur est root. Si ce n'est pas le cas, affiche un message d'erreur et quitte le script.
    """
    if os.geteuid() != 0:
        print('This script must be run as root!')
        sys.exit(1)

def load_yaml_file(file_path):
    """
    Charge le fichier YAML et retourne son contenu.
    """
    with open(file_path) as f:
        return yaml.load(f, Loader=yaml.FullLoader)

def get_packages_to_install(data, category, subcategories):
    """
    Retourne la liste des packages à installer en fonction de la catégorie et des sous-catégories spécifiées.
    """
    packages = []
    for subcategory in subcategories:
        if subcategory in data[category]:
            packages += data[category][subcategory]
    if 'other_packages' in data[category]:
        packages += data[category]['other_packages']
    
    # Remplacer le mot clé 'linux_headers' par 'linux-headers-$(uname -r)'
    if 'linux_headers' in packages:
        packages.remove('linux_headers')
        linux_headers_pkg = f'linux-headers-{os.uname().release}'
        packages.append(linux_headers_pkg)
    
    # Supprime les doublons
    return list(set(packages))

def check_last_update():
    """
    Vérifie l'heure du dernier apt-get update et le met à jour si nécessaire.
    """
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

def main():
    """
    Fonction principale du script. Analyse les arguments de la ligne de commande, charge le fichier YAML, installe les packages et affiche un message de succès.
    """
    args = parse_arguments()
    check_root()
    data = load_yaml_file(args.file)
    if args.category not in data:
        print(f'Category "{args.category}" not found in the YAML file!')
        sys.exit(1)
    packages = get_packages_to_install(data, args.category, args.subcategories)
    check_last_update()
    install_packages(packages)
    print('Success!')
    sys.exit(0)
    
if __name__ == '__main__':
    main()
