"""
Test fixtures for alienlogger tests.  Sets up information for testing.
"""
import os
from pathlib import Path
from typing import Optional
import pytest


class TestContext:
    """
    Context which wraps a whole bunch of testing stateful stuff for use within unit tests.
    """

    """
    We infer the root path of the project, from this we can get the collateral paths etc.
    """
    project_path: Path

    """
    The path to the test collateral, which is used in testing.  
    """
    test_collateral_path: Path

    log_config_path: Path

    def __init__(self, log_config_path: Path):
        """
        Constructor for the test context, finds the project path and sets things up.
        """
        self.project_path = get_project_dir()
        assert self.project_path.exists(), f"Project path should exist! {self.project_path}"

        #
        # Setup the configuration files
        #
        self.log_config_path: Path = log_config_path
        assert self.log_config_path.exists(), f"Config File path for testing should exist!  {self.log_config_path}"

def get_project_dir() -> Optional[Path]:
    """
    Figure out what is the project directory, to figure out the collateral path..
    :return: The project dir that was found, or None if not found.
    """
    #
    # Start from the current directory and crawl up (up to 10 levels) and try to find
    # the .gitignore file, which we know is at the root.
    #
    cur_path = Path(os.curdir).resolve().absolute()
    for level in range(0,10):
        if cur_path.joinpath('.gitignore').exists():
            return cur_path.resolve().absolute()

        if not cur_path.parent:
            return None

        cur_path = cur_path.parent

    return None

@pytest.fixture
def test_context():
    """
    Returns a test context which requires everything needed for testing.
    :return: The test context.
    """

    project_dir = get_project_dir()
    config_file = project_dir.joinpath('testing/collateral/testing/test_alienlogger_config.toml')
    os.environ['ALIENLOGGER__CONFIG_FILE_PATH'] = str(config_file)
    return TestContext(log_config_path=config_file)