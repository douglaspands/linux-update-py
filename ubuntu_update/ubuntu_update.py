from __future__ import annotations

import subprocess
from pathlib import Path
from uuid import uuid4


class UbuntuUpdate:
    CMD_OK = 0
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
        self._temp_files: list[Path] = []

    def _shell(self, cmds: str | list[str], show_output: bool = True) -> int:
        cmd = " && ".join(cmds) if isinstance(cmds, list) else cmds
        return subprocess.run(
            cmd, shell=True, capture_output=show_output is False
        ).returncode

    def _check_application(self, app_name: str) -> bool:
        if self._shell(f"type {app_name}", show_output=False) == UbuntuUpdate.CMD_OK:
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
        file.write_text(UbuntuUpdate.SH_SNAP_REMOVE)
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
        return ["brew cleanup --prune=all"]

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

    def __enter__(self):
        return self

    def __exit__(self, exc_type=None, exc_value=None, traceback=None):
        self.temp_clean()
        if exc_value:
            raise exc_value

    def temp_clean(self):
        for file in self._temp_files:
            file.unlink(missing_ok=True)

    def update(self, app: str):
        cmds = []
        if app == "all" or app == "apt":
            cmds += self._apt_upgrade() + self._apt_clean()
        elif app == "all" or app == "snap":
            cmds += self._snap_upgrade() + self._snap_clean()
        elif app == "all" or app == "flatpak":
            cmds += self._flatpak_upgrade() + self._flatpak_clean()
        print(">> UBUNTU UPDATE STARTED\n")
        self._shell(cmds)
        print("\n>> UBUNTU UPDATE COMPLETED")


__all__ = ("UbuntuUpdate",)
