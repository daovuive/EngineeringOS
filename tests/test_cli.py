from engineering_os.cli import main


def test_version_command_returns_success() -> None:
    assert main(["version"]) == 0
