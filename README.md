# Distro Upgrade
Ferramenta de apoio a atualização de Distros baseadas em Linux.

## Requisitos
- Python 3.12 ou superior;
- Sistema operacionais baseados em Linux;
> Suportado apenas distros baseadas no Debian e no Arch.   
> Empacotadores: snap, flatpak e brew.

## Como usar
```sh
❯ python distro_upgrade.py all
```
ou
```sh
❯ ./distro_upgrade.py all
```

### help
```sh
❯ python distro_upgrade.py --help 
usage: distro_upgrade.py [-h] {all,apt,brew,flatpak,pacman,snap,yay}

positional arguments:
  {all,apt,brew,flatpak,pacman,snap,yay}
                        Update applications and all dependencies.

options:
  -h, --help            show this help message and exit
```
