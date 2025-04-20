# Ubuntu Update
Ferramenta de apoio a atualização do Ubuntu e seus derivados.

## Requisitos
- Python 3.12 ou superior
- Sistema operacional Linux baseado no Ubuntu (Ubuntu, Debian, Mint, etc...)

## Como usar
```sh
❯ python main.py update --help 
usage: main.py update [-h] {apt,snap,flatpak,all}

positional arguments:
  {apt,snap,flatpak,all}
                        Update the application and all installed packages.

options:
  -h, --help            show this help message and exit
```