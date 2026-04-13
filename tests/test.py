from subprocess import run
from pathlib import Path
from os import remove
from shutil import rmtree

def create_files(paths: list[Path]):
    for path in paths:
        path.touch()

def remove_files(paths: list[Path]):
    for path in paths:
        if path.exists():
            if path.is_dir():
                rmtree(path)
            else:
                remove(path)

# Wrapper for subprocess.run with shell=True
# & optional capture_output, env prefix & env var resetting
def filecat(command: str, prefix:str=None, capture_output:bool=False):
    command = f"python src/filecat.py {command}"
    if prefix:
        command = prefix + " " + command
    command = "unset FILECAT_TRASH && " + command
    return run(command, shell=True, capture_output=capture_output)


def _trashpress_works_as_expected(prefix=None, suffix="",
    EXPECTED_DIR: Path=Path().home().joinpath("./.filecat/trash")):

    RELATIVE_PATH = Path("testfile-1")
    ABSOLUTE_PATH = Path("testfile-2").absolute()
    INPUT_FILES = [RELATIVE_PATH, ABSOLUTE_PATH]

    TRASHPRESSED_RELATIVE_PATH = EXPECTED_DIR.joinpath("testfile-1.tar.gz")
    TRASHPRESSED_ABSOLUTE_PATH = EXPECTED_DIR.joinpath("testfile-2.tar.gz")
    EXPECTED_FILES = [TRASHPRESSED_RELATIVE_PATH, TRASHPRESSED_ABSOLUTE_PATH]

    # Setup
    create_files(INPUT_FILES)
    remove_files(EXPECTED_FILES)

    # Test relative & absolute paths
    assert RELATIVE_PATH.exists() and ABSOLUTE_PATH.exists()
    assert not TRASHPRESSED_RELATIVE_PATH.exists() and not TRASHPRESSED_ABSOLUTE_PATH.exists()
    # INPUT: y
    filecat(f"trashpress {suffix} {RELATIVE_PATH} {ABSOLUTE_PATH}", prefix)
    assert not RELATIVE_PATH.exists()
    assert not ABSOLUTE_PATH.exists()
    assert TRASHPRESSED_RELATIVE_PATH.exists()
    assert TRASHPRESSED_ABSOLUTE_PATH.exists()
    
    create_files(INPUT_FILES)
    remove_files(EXPECTED_FILES)

    # Cleanup
    remove_files(INPUT_FILES + EXPECTED_FILES)

def test_trashpress():
    # Default setup
    _trashpress_works_as_expected()  # INPUT: y
    
    # Using --trash arg, relative dir
    RELATIVE_TRASH_DIR = Path(".test-trash/")
    remove_files([RELATIVE_TRASH_DIR])
    assert not RELATIVE_TRASH_DIR.exists()
    # INPUT: y
    _trashpress_works_as_expected(None, f"--trash \'{RELATIVE_TRASH_DIR}\'", RELATIVE_TRASH_DIR)

    # Using FILECAT_TRASH env var
    ABSOLUTE_TRASH_DIR = Path(".testtrash/").absolute()
    remove_files([ABSOLUTE_TRASH_DIR])
    assert not ABSOLUTE_TRASH_DIR.exists()
    # INPUT: y
    _trashpress_works_as_expected(f"FILECAT_TRASH='{ABSOLUTE_TRASH_DIR}'", "", ABSOLUTE_TRASH_DIR)
    remove_files([ABSOLUTE_TRASH_DIR])

    # Selecting no
    should_not_be_trashed = Path("test_file")
    create_files([should_not_be_trashed])
    assert should_not_be_trashed.exists()
    filecat("trashpress test_file")  # INPUT: n
    assert should_not_be_trashed.exists()
    remove_files([should_not_be_trashed])


def test_checksum():
    print(filecat("checksum tests/data/same-as-1/file", None, True).stdout)

if __name__ == "__main__":
    test_trashpress()   # INPUT: ynyy

    test_checksum()