# Linux Update
Ferramenta de apoio a atualização de Distros baseadas em Linux.

## Requisitos
- Python 3.12 ou superior;
- Sistema operacionais baseados em Linux;
> Suportado apenas distros baseadas no Debian e no Arch.   
> Empacotadores: snap, flatpak e brew.

## Como usar
```sh
❯ python main.py update all
```
ou
```sh
❯ ./main.py update all
```

### help
```sh
❯ python main.py update --help 
usage: main.py update [-h] {all,apt,brew,flatpak,pacman,snap,yay}

positional arguments:
  {all,apt,brew,flatpak,pacman,snap,yay}
                        Update applications and all dependencies.

options:
  -h, --help            show this help message and exit
```