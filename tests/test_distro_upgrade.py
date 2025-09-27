from __future__ import annotations

import runpy
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.distro_upgrade import DistroUpgrade, main


@pytest.fixture
def distro_upgrade():
    with DistroUpgrade() as du:
        yield du


def test_shell(distro_upgrade: DistroUpgrade, capsys):
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        result = distro_upgrade._shell("ls")
        assert result == 0
        mock_run.assert_called_once_with("ls", shell=True, capture_output=False)


def test_shell_isolate(distro_upgrade: DistroUpgrade, capsys):
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        distro_upgrade._shell_isolate(["ls", "pwd"])
        assert mock_run.call_count == 2
        mock_run.assert_any_call("ls", shell=True, capture_output=False)
        mock_run.assert_any_call("pwd", shell=True, capture_output=False)


def test_check_application(distro_upgrade: DistroUpgrade):
    with patch.object(distro_upgrade, "_shell") as mock_shell:
        mock_shell.return_value = 0
        assert distro_upgrade._check_application("git") is True
        mock_shell.assert_called_once_with("type git", show_output=False)

        mock_shell.return_value = 1
        assert distro_upgrade._check_application("nonexistent") is False


def test_available_managers(distro_upgrade: DistroUpgrade):
    with patch.object(distro_upgrade, "_check_application") as mock_check:
        mock_check.side_effect = lambda app: app in ["apt", "snap"]
        assert sorted(distro_upgrade.available_managers()) == ["all", "apt", "snap"]


def test_available_managers_no_managers(distro_upgrade: DistroUpgrade):
    with patch.object(distro_upgrade, "_check_application", return_value=False):
        assert distro_upgrade.available_managers() == []


@pytest.mark.parametrize(
    "package_manager", ["apt", "pacman", "yay", "snap", "flatpak", "brew"]
)
def test_upgrade_package_managers(distro_upgrade: DistroUpgrade, package_manager: str):
    with (
        patch.object(
            distro_upgrade, "_available_managers", return_value=[package_manager]
        ),
        patch.object(distro_upgrade, "_shell_isolate") as mock_shell_isolate,
    ):
        distro_upgrade.upgrade(package_manager)
        mock_shell_isolate.assert_called_once()


def test_upgrade_all(distro_upgrade: DistroUpgrade):
    with (
        patch.object(
            distro_upgrade, "_available_managers", return_value=["apt", "snap"]
        ),
        patch.object(distro_upgrade, "_shell_isolate") as mock_shell_isolate,
    ):
        distro_upgrade.upgrade("all")
        assert mock_shell_isolate.call_count == 1


def test_upgrade_invalid_app(distro_upgrade: DistroUpgrade):
    with patch.object(distro_upgrade, "_available_managers", return_value=["apt"]):
        with pytest.raises(ValueError, match="Invalid app: brew"):
            distro_upgrade.upgrade("brew")


def test_temp_clean(distro_upgrade: DistroUpgrade):
    mock_path = MagicMock(spec=Path)
    distro_upgrade._temp_files.append(mock_path)
    distro_upgrade._update_started = True
    distro_upgrade.temp_clean()
    mock_path.unlink.assert_called_once_with(missing_ok=True)


def test_context_manager():
    with patch.object(DistroUpgrade, "temp_clean") as mock_temp_clean:
        with DistroUpgrade() as du:
            pass
        mock_temp_clean.assert_called_once()

    with patch.object(DistroUpgrade, "temp_clean") as mock_temp_clean:
        with pytest.raises(ValueError):
            with DistroUpgrade() as du:
                raise ValueError("test error")
        mock_temp_clean.assert_called_once()


def test_main_block():
    with (
        patch("distro_upgrade.argparse.ArgumentParser") as mock_parser,
        patch("distro_upgrade.DistroUpgrade") as mock_distro_upgrade_class,
        patch("sys.argv", ["distro_upgrade.py", "all"]),
        patch("builtins.print"),
    ):
        mock_instance = mock_distro_upgrade_class.return_value.__enter__.return_value
        mock_instance.available_managers.return_value = ["all", "apt"]

        mock_args = MagicMock()
        mock_args.package = "all"
        mock_parser.return_value.parse_args.return_value = mock_args

        main()

        mock_instance.upgrade.assert_called_once_with(app="all")


def test_main_no_args():
    with (
        patch("distro_upgrade.argparse.ArgumentParser") as mock_parser,
        patch("sys.argv", ["distro_upgrade.py"]),
        patch("sys.exit") as mock_exit,
        patch("builtins.print"),
    ):
        mock_parser_instance = mock_parser.return_value
        mock_exit.side_effect = SystemExit

        with pytest.raises(SystemExit):
            main()

        mock_parser_instance.print_help.assert_called_once()
        mock_exit.assert_called_once_with(1)


def test_main_entrypoint():
    with (
        patch("sys.argv", ["distro_upgrade.py", "all"]),
        patch("distro_upgrade.DistroUpgrade") as mock_distro_upgrade_class,
    ):
        mock_instance = mock_distro_upgrade_class.return_value.__enter__.return_value
        mock_instance.available_managers.return_value = ["all", "apt"]

        runpy.run_module("distro_upgrade", run_name="__main__")

        mock_distro_upgrade_class.assert_called_once()
        mock_instance.upgrade.assert_called_once_with(app="all")
