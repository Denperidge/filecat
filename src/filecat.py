from subprocess import run as _run
from argparse import ArgumentParser
from time import sleep
from pathlib import Path
from shutil import rmtree
from os import remove, environ, makedirs
from traceback import format_exception
import curses

"""SECTION: logging"""
# Wrapper for print allowing terminal colour codes
def _print_colour(message: str, colourCode: int|str):
    print(f"\x1b[{colourCode}m{message}\x1b[0m")

# Wrapper for _print_colour with green pre-set
def print_green(message: str):
    _print_colour(message, 32)

# Wrapper for _print_colour with red pre-set
def print_red(message: str):
    _print_colour(message, 31)

# Wrapper around print(_green), with newline & underline
def header(text: str):
    print()
    print_green(text)
    print_green("-" * len(text))

"""SECTION: Program utils"""
# Parses a list of Path objects, checking
# if any passed filepaths are in non-usual locations
# E.G. not home directory & not a mounted drive
usual_paths = [str(Path.home().absolute()), "/mnt/"]
def check_all_usual_paths(files: list[str]):
    for file in files:
        file_path = str(Path(file).absolute())
        file_path_is_usual = False
        for usual_path in usual_paths:
            if file_path.startswith(usual_path) and file_path != usual_path:
                file_path_is_usual = True
                break
        # If every usual path is checked and none match,
        if not file_path_is_usual:
            return False  # A single unsual path is found, return False
    # If every path is starts with one of the usual paths, return True
    return True

# Wrapper for subprocess.run
# with shell=True & optional manual cwd
def run(command: str, cwd:str=None, capture_output=False):
    if cwd:
        script = f"cd '{cwd}' && " + command
    return _run(command, shell=True, encoding="UTF-8", capture_output=capture_output)

"""Section: Confirming & GUI"""
CURSES_SCREEN = False
def setup_curses():
    screen = curses.initscr()  # Initialize
    curses.noecho()
    curses.cbreak()  # Don't require ENTER
    return screen

# Curses screen to ask for confirmation
# If the answer is y or Y, return True
# Else, return False
def confirm(message: str):
    global CURSES_SCREEN
    if not CURSES_SCREEN:
        CURSES_SCREEN = setup_curses()
    
    CURSES_SCREEN.clear()
    CURSES_SCREEN.addstr(message + "\n\n[y/N]: ")
    CURSES_SCREEN.refresh()

    selection = CURSES_SCREEN.getkey().lower()
    curses.endwin()
    
    return selection == "y"

"""SECTION: commands"""
def trashpress(files: list[Path], trash_dir: Path):
    if not trash_dir.exists():
        makedirs(str(trash_dir.absolute()), exist_ok=True)

    extra_message = "" if check_all_usual_paths(files) else "\n\nWARNING: at least one of the selected paths are not in a regular user directory"
    if not confirm(f"Are you sure you want to compress the following files to {trash_dir}?{extra_message}\n\n[ {', '.join([str(file) for file in files])} ]"):
        return

    for file in files:
        if not file.is_dir():
            output_name = file.name
        else:
            output_name = file.name + ".dir"
        header(f"Archiving {file.name} to {trash_dir}")
        run(f'tar -czvf "{trash_dir}/{output_name}.tar.gz" "{file.relative_to(file.parent)}"', file.parent)
        header("Removing original file...")
        if file.is_dir():
            rmtree(file.absolute())
        else:
            remove(file.absolute())

def checksum(files: list[Path], checksumtool: str, include_filenames: bool=True):
    results = []
    errors = []
    for file in files:
        if file.is_dir():
            # If directory, calculate checksums for every 
            print(f"Traversing directory: {file}")
            results += checksum(list(file.glob("*")), checksumtool)
        else:
            # If individual file, calculate checksum
            print(f"Calculating checksum: {file}")
            instance = run(f"{checksumtool} {file}", None, capture_output=True)
            
            if include_filenames:
                result = instance.stdout.strip()
            else:
                result = instance.stdout.split(" ")[0].strip()
                print("@@@")
            results.append(result)
            error = instance.stderr.strip()
            if error != "":
                errors.append(instance.stderr.strip())

    if len(errors) > 0:
        input("Press ENTER to close...")
        print_red(f"'{"\n".join(errors)}'")
    return results

def samesies(files: list[Path], checksumtool: str):
    if len(files) < 2:
        print_red("[samesies] needs at least 2 files to be passed!")
        raise Exception()
    control_file = files.pop()
    control_results = checksum([control_file], checksumtool, include_filenames=False)
    control_hashes = "\n".join(control_results)

    for file in files:
        results = checksum([file], checksumtool, include_filenames=False)
        hashes = "\n".join(results)
        if hashes != control_hashes:
            raise Exception(f"Hashes for {control_file} & {file} are not the same:\n[{control_file}] '{control_hashes}'\nIs not the same as\n[{file}] '{hashes}')")
    
    fileprint = [str(path) for path in files + [control_file]]
    print_green(f"{" == ".join(fileprint)}")


commands = {
    "trashpress": trashpress,
    "checksum": checksum,
    "samesies": samesies
}

"""SECTION: command-line interface"""
if __name__ == "__main__":
    # Parse arguments
    parser = ArgumentParser(prog="filecat",
        usage="python filecat.py --help",
        description=f"A file management CLI for CLI tool popup integrations in the file browser. Designed to integrate with Nemo actions: see the repo for an example action")
    parser.add_argument("command", choices=commands.keys())
    parser.add_argument("files", nargs="*")
    parser.add_argument("--trash", "-t",
        default=environ.get("FILECAT_TRASH", Path.home().joinpath("./.filecat/trash/")),
        help="[trashpress], directory to move compressed files to. Defaults to the FILECAT_TRASH env var if defined, otherwise ~/.filecat/trash/")
    parser.add_argument("--checksumtool", "-c",
        default=environ.get("FILECAT_CHECKSUMTOOL", "sha512sum"),
        help="[checksum, samesies] Executable to be used for checksum calculations. Needs to be in PATH or a full path. Defaults to FILECAT_CHECKSUMTOOL if set, otherwise sha512sum")

    args = parser.parse_args()

    # Parse file parameters into Path objects
    files = [Path(path) for path in args.files]

    # Pass the file parameters to the command
    try:
        match args.command:
            case "trashpress":
                trashpress(files, trash_dir=Path(args.trash))
            case "checksum":
                results = checksum(files, checksumtool=args.checksumtool)
                for result in results:
                    print(result)
            case "samesies":
                samesies(files, checksumtool=args.checksumtool)
    # If an error occurs during the command,
    # print it in red and require ENTER to continue
    except Exception as e:
        print_red("Error whilst using filecat " + args.command)
        traceback_lines = format_exception(e)  # Based on https://stackoverflow.com/a/3702847
        for trace in traceback_lines:
            print_red(trace)
        input("Press ENTER to close...")
        raise e
