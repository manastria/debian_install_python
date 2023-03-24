# Package Installer

This Python script installs packages on a Debian-based Linux system using the `apt-get` command. It reads a list of packages to install from a YAML file and installs them along with their dependencies.

## Prerequisites

- Python 3.x
- `apt-get` package manager
- YAML module (`pyyaml`) for Python

## Usage

```css
sudo python3 package_installer.py [-h] [-f FILE] [-c CATEGORY] [-s [SUBCATEGORIES [SUBCATEGORIES ...]]]
```

### Optional arguments:

- `-h`, `--help`: show this help message and exit
- `-f FILE`, `--file FILE`: path to the YAML file containing the packages to install (default: `packages.yaml`)
- `-c CATEGORY`, `--category CATEGORY`: name of the category to install
- `-s [SUBCATEGORIES [SUBCATEGORIES ...]]`, `--subcategories [SUBCATEGORIES [SUBCATEGORIES ...]]`: name of the subcategories to install (default: `[]`)

### Example

```r
sudo python3 package_installer.py -c web -s server tools
```

This command will install the packages listed in the `web` category, specifically those in the `server` and `tools` subcategories, as defined in the `packages.yaml` file.

## YAML File

The YAML file contains a list of packages organized by category and subcategory. Here is an example:

```yaml
web:
  server:
    - apache2
    - nginx
  tools:
    - curl
    - wget
  other_packages:
    - htop
```

Each category and subcategory is a dictionary, with the subcategories and other packages keys being optional. The values are lists of package names.

## Cache Update

The script updates the package cache every two hours by default to ensure that the latest package information is used during installation. You can adjust this interval by changing the value of `CACHE_UPDATE_INTERVAL` (in seconds) at the beginning of the script.

## License

This script is released under the [MIT License](https://opensource.org/licenses/MIT).
