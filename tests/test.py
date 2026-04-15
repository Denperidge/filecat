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
    return run(command, shell=True, encoding="UTF-8", capture_output=capture_output)


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
    # Test individual file checksum & --checksumtool
    EXPECTED_SHA512 = "0988e7e7c71dc7fc8238c2a17e6849cacc891d546cfb4912e4a242697ce0a66f92aebec5051eeb795b46fa1e8571d974ae3095ab721b6c68e25e91c67025e813  tests/data/same-as-1/file\n"
    EXPECTED_MD5 = "cef5182f29745373f1922d6c7f801445  tests/data/same-as-1/file\n"
    file_sha512 = filecat("checksum tests/data/same-as-1/file", None, True).stdout
    file_md5 = filecat("checksum --checksumtool md5sum tests/data/same-as-1/file", None, True).stdout

    assert file_sha512.endswith(EXPECTED_SHA512)  # Don't include header/process info; check the end
    assert file_md5.endswith(EXPECTED_MD5)

    # Test directory
    EXPECTED_DIRECTORY = """cd555551b68c0a28e97af5265013113c120b89c604860511a0c330c19303d0bc374b2362802c19db3e993746e42f1ae63ddd080b6ebb108a756791d3d28dae40  tests/data/different-than-both/meow
c2d4ece00176bf7a01da1cf0f8170d237e3b34595de99289a9c108fabdaeb481bbd1cd1bf3193f9f198b8b23becfbf686ca36237a57769d8591c7f94bd2f944a  tests/data/different-than-both/sub/subdir/bark
0988e7e7c71dc7fc8238c2a17e6849cacc891d546cfb4912e4a242697ce0a66f92aebec5051eeb795b46fa1e8571d974ae3095ab721b6c68e25e91c67025e813  tests/data/same-as-2/file
43230baa9cf7d68a0a0377e2a3b4b5ba7dc985f3e4b3c6a39e3351531abab92eb8abbb63b373155bcda0ce3e6259524ac663175155e1144cfa923d49c6e2f634  tests/data/same-as-2/subdir/otherfile
0988e7e7c71dc7fc8238c2a17e6849cacc891d546cfb4912e4a242697ce0a66f92aebec5051eeb795b46fa1e8571d974ae3095ab721b6c68e25e91c67025e813  tests/data/same-as-1/file
43230baa9cf7d68a0a0377e2a3b4b5ba7dc985f3e4b3c6a39e3351531abab92eb8abbb63b373155bcda0ce3e6259524ac663175155e1144cfa923d49c6e2f634  tests/data/same-as-1/subdir/otherfile\n"""
    directory_sha512 = filecat("checksum tests/data/", None, True).stdout

    assert directory_sha512.endswith(EXPECTED_DIRECTORY)
    assert EXPECTED_SHA512 in directory_sha512

    same_as_1 = filecat("checksum tests/data/same-as-1/", None, True).stdout
    same_as_2 = filecat("checksum tests/data/same-as-2/", None, True).stdout
    different_than_both = filecat("checksum tests/data/different-than-both/", None, True).stdout

    # Two directories with identical contents have consistent results, minus the part being different
    assert same_as_1 == same_as_2.replace("same-as-2", "same-as-1")
    # Sanity check
    assert same_as_1 != different_than_both
    assert same_as_2 != different_than_both


def test_samesies():
    from json import dumps
    result = filecat("samesies tests/data/same-as-1/file tests/data/same-as-2/file", None, True)
    assert result.stdout.endswith("tests/data/same-as-2/file == tests/data/same-as-1/file\u001b[0m\n")
    assert result.returncode == 0
    # Errrors on non-identical files
    try:
        # INPUT: \n
        should_error = filecat("samesies tests/data/same-as-1/file tests/data/different-than-both/meow", None, True)
        assert False  # If no error is throw, something is wrong
    except:
        assert should_error.returncode == 1

if __name__ == "__main__":
    test_trashpress()   # INPUT: yyyn
    test_checksum()
    test_samesies()  # INPUT: \n