# Linux Update
Ferramenta de apoio a atualização de Distros baseadas em Linux.

## Requisitos
- Python 3.12 ou superior;
- Sistema operacionais baseados em Linux;
> Suportado apenas distros baseadas no Debian e no Arch.   
> Empacotadores: snap, flatpak e brew.

## Como usar
```sh
❯ python main.py update --help 
usage: main.py update [-h] {apt,pacman,yay,snap,flatpak,brew,all}

positional arguments:
  {apt,pacman,yay,snap,flatpak,brew,all}
                        Update the application and all installed packages.

options:
  -h, --help            show this help message and exit
```