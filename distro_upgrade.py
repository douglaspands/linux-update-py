#! /usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
from pathlib import Path
from time import perf_counter as time
from uuid import uuid4


class DistroUpgrade:
    CMD_OK = 0
    MANAGERS_SUPPORTED = ("apt", "pacman", "yay", "snap", "flatpak", "brew")
    SH_SNAP_REMOVE = r"""
set -eu
snap list --all | awk '/disabled/{print $1, $3}' |
    while read snapname revision; do
        sudo snap remove "$snapname" --revision="$revision"
    done
        """.strip()

    def __init__(self):
        self._temp_files: list[Path] = []
        self._update_started = False
        self._available: set[str] = set()

    def _shell(self, cmds: str | list[str], show_output: bool = True) -> int:
        cmd = " && ".join(cmds) if isinstance(cmds, list) else cmds
        # print(f"{cmd=}")
        return subprocess.run(
            cmd, shell=True, capture_output=show_output is False
        ).returncode

    def _shell_isolate(self, cmds: str | list[str], show_output: bool = True):
        cmds = cmds if isinstance(cmds, list) else [cmds]
        for cmd in cmds:
            # print(f"{cmd=}")
            subprocess.run(
                cmd, shell=True, capture_output=show_output is False
            ).returncode

    def _check_application(self, app_name: str) -> bool:
        if self._shell(f"type {app_name}", show_output=False) == DistroUpgrade.CMD_OK:
            return True
        else:
            return False

    def _apt_upgrade(self) -> list[str]:
        return ["sudo apt -y update", "sudo apt -y upgrade"]

    def _apt_clean(self):
        return ["sudo apt -y autoremove", "sudo apt -y autoclean"]

    def _snap_upgrade(self):
        return ["sudo snap refresh"]

    def _snap_clean(self):
        file = Path(f"./{uuid4()}.sh")
        self._temp_files.append(file)
        file.write_text(DistroUpgrade.SH_SNAP_REMOVE)
        return [f"sudo sh {file.resolve()!s}"]

    def _brew_upgrade(self):
        return [
            "brew update",
            "brew upgrade",
        ]

    def _brew_clean(self):
        return ["brew cleanup"]

    def _flatpak_upgrade(self):
        return [
            "flatpak update -y",
        ]

    def _flatpak_clean(self):
        return [
            "flatpak uninstall --unused -y",
            "sudo rm -rfv /var/tmp/flatpak-cache-*",
        ]

    def _pacman_upgrade(self) -> list[str]:
        return ["sudo pacman --noconfirm -Syu"]

    def _pacman_clean(self):
        return [
            "sudo pacman --noconfirm -Rs $(pacman -Qtdq)",
            "sudo pacman --noconfirm -Sc",
        ]

    def _yay_upgrade(self) -> list[str]:
        return ["yay -Syu --noconfirm"]

    def _yay_clean(self):
        return ["yay -Rs $(yay -Qtdq)", "yay --noconfirm -Sc"]

    def __enter__(self):
        return self

    def __exit__(self, exc_type=None, exc_value=None, traceback=None):
        self.temp_clean()
        if exc_value:
            raise exc_value

    def temp_clean(self):
        if self._update_started:
            for file in self._temp_files:
                file.unlink(missing_ok=True)

    def upgrade(self, app: str):
        self._update_started = True
        choices = self._available_managers()
        cmds = []
        if app in ("all", "apt") and "apt" in choices:
            cmds += self._apt_upgrade() + self._apt_clean()
        if app in ("all", "pacman") and "pacman" in choices:
            cmds += self._pacman_upgrade() + self._pacman_clean()
        if app in ("all", "yay") and "yay" in choices:
            cmds += self._yay_upgrade() + self._yay_clean()
        if app in ("all", "snap") and "snap" in choices:
            cmds += self._snap_upgrade() + self._snap_clean()
        if app in ("all", "flatpak") and "flatpak" in choices:
            cmds += self._flatpak_upgrade() + self._flatpak_clean()
        if app in ("all", "brew") and "brew" in choices:
            cmds += self._brew_upgrade() + self._brew_clean()
        else:
            raise ValueError(f"Invalid app: {app}")

        self._shell_isolate(cmds)

    def _available_managers(self) -> list[str]:
        if not self._available:
            for manager in DistroUpgrade.MANAGERS_SUPPORTED:
                if self._check_application(manager):
                    self._available.add(manager)
        return list(self._available)

    def available_managers(self) -> list[str]:
        available = self._available_managers()
        if len(available):
            available.append("all")
        return sorted(available)


if __name__ == "__main__":
    with DistroUpgrade() as distro_upgrade:
        parser = argparse.ArgumentParser(description="Distro Linux Upgrade")
        parser.add_argument(
            "package",
            help="Packages upgrade using the chosen package manager.",
            choices=distro_upgrade.available_managers(),
        )

        args = parser.parse_args()
        print(">> Distro Linux upgrade started\n")

        time_start = time()
        distro_upgrade.upgrade(app=args.package)
        time_total = time() - time_start

        print(f"\n>> Total time taken: {time_total:.2f} seconds")
        print(">> Distro Linux upgrade completed")
