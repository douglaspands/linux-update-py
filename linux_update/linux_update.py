from __future__ import annotations

import subprocess
from pathlib import Path
from uuid import uuid4


class LinuxUpdate:
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
        self._has_apt: bool | None = None
        self._has_snap: bool | None = None
        self._has_brew: bool | None = None
        self._has_flatpak: bool | None = None
        self._has_pacman: bool | None = None
        self._has_yay: bool | None = None
        self._temp_files: list[Path] = []
        self._startd = False

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
        if self._shell(f"type {app_name}", show_output=False) == LinuxUpdate.CMD_OK:
            return True
        else:
            return False

    def _apt_upgrade(self) -> list[str]:
        if self._has_apt is None:
            self._has_apt = self._check_application("apt")
        if not self._has_apt:
            return []
        return ["sudo apt -y update", "sudo apt -y upgrade"]

    def _apt_clean(self):
        if self._has_apt is None:
            self._has_apt = self._check_application("apt")
        if not self._has_apt:
            return []
        return ["sudo apt -y autoremove", "sudo apt -y autoclean"]

    def _snap_upgrade(self):
        if self._has_snap is None:
            self._has_snap = self._check_application("snap")
        if not self._has_snap:
            return []
        return ["sudo snap refresh"]

    def _snap_clean(self):
        if self._has_snap is None:
            self._has_snap = self._check_application("snap")
        if not self._has_snap:
            return []
        file = Path(f"./{uuid4()}.sh")
        self._temp_files.append(file)
        file.write_text(LinuxUpdate.SH_SNAP_REMOVE)
        return [f"sudo sh {file.resolve()!s}"]

    def _brew_upgrade(self):
        if self._has_brew is None:
            self._has_brew = self._check_application("brew")
        if not self._has_brew:
            return []
        return [
            "brew update",
            "brew upgrade",
        ]

    def _brew_clean(self):
        if self._has_brew is None:
            self._has_brew = self._check_application("brew")
        if not self._has_brew:
            return []
        return ["brew cleanup"]

    def _flatpak_upgrade(self):
        if self._has_flatpak is None:
            self._has_flatpak = self._check_application("flatpak")
        if not self._has_flatpak:
            return []
        return [
            "flatpak update -y",
        ]

    def _flatpak_clean(self):
        if self._has_flatpak is None:
            self._has_flatpak = self._check_application("flatpak")
        if not self._has_flatpak:
            return []
        return [
            "flatpak uninstall --unused -y",
            "sudo rm -rfv /var/tmp/flatpak-cache-*",
        ]

    def _pacman_upgrade(self) -> list[str]:
        if self._has_pacman is None:
            self._has_pacman = self._check_application("pacman")
        if not self._has_pacman:
            return []
        return ["sudo pacman -Syu --noconfirm"]

    def _pacman_clean(self):
        if self._has_pacman is None:
            self._has_pacman = self._check_application("pacman")
        if not self._has_pacman:
            return []
        return ["sudo pacman -Rs $(pacman -Qtdq)", "sudo pacman --noconfirm -Sc"]

    def _yay_upgrade(self) -> list[str]:
        if self._has_yay is None:
            self._has_yay = self._check_application("yay")
        if not self._has_yay:
            return []
        return ["yay -Syu --noconfirm"]

    def _yay_clean(self):
        if self._has_yay is None:
            self._has_yay = self._check_application("yay")
        if not self._has_yay:
            return []
        return ["yay -Rs $(yay -Qtdq)", "yay --noconfirm -Sc"]

    def __enter__(self):
        return self

    def __exit__(self, exc_type=None, exc_value=None, traceback=None):
        self.temp_clean()
        if exc_value:
            raise exc_value

    def temp_clean(self):
        if self._startd:
            for file in self._temp_files:
                file.unlink(missing_ok=True)

    def update(self, app: str):
        self._startd = True
        cmds = []
        if app == "all" or app == "apt":
            cmds += self._apt_upgrade() + self._apt_clean()
        if app == "all" or app == "pacman":
            cmds += self._pacman_upgrade() + self._pacman_clean()
        if app == "all" or app == "yay":
            cmds += self._yay_upgrade() + self._yay_clean()
        if app == "all" or app == "snap":
            cmds += self._snap_upgrade() + self._snap_clean()
        if app == "all" or app == "flatpak":
            cmds += self._flatpak_upgrade() + self._flatpak_clean()
        if app == "all" or app == "brew":
            cmds += self._brew_upgrade() + self._brew_clean()
        else:
            raise ValueError(f"Invalid app: {app}")
        print(">> LINUX DISTRO UPGRADE STARTED\n")
        self._shell_isolate(cmds)
        print("\n>> LINUX DISTRO UPGRADE COMPLETED")

    def available_managers(self) -> list[str]:
        available = []
        for manager in LinuxUpdate.MANAGERS_SUPPORTED:
            if self._check_application(manager):
                available.append(manager)
        return available


__all__ = ("LinuxUpdate",)
