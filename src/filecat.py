from subprocess import run as _run
from argparse import ArgumentParser
from time import sleep
from pathlib import Path
from shutil import rmtree
from os import remove, environ, makedirs

"""
Example action
~/.local/share/nemo/actions/trash_and_compress.nemo_action
----------------------------------------------------------
[Nemo Action]
Name=Trash & Compress
Comment=Trash & Compress
Exec=alacritty-run "Trashpress" 'python /home/user/.local/share/nemo/actions/filecat.py trashpress %F'
Quote=double
Icon-Name=bug-buddy
Selection=Any
Extensions=any
"""

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
def run(command: str, cwd:str=None):
    if cwd:
        script = f"cd '{cwd}' && " + command
    return _run(command, shell=True)

# Wrapper for run & zenity to ask for confirmation
# If the return code is 0 (success), return True
# Else, return False
def confirm(message: str):
    return run(f"zenity --question --text='{message}'").returncode == 0

"""SECTION: commands"""
TRASH = environ.get("FILECAT_TRASH", Path.home().joinpath("./.filecat/trash/"))

def trashpress(files: list[str]):
    if not TRASH.exists():
        makedirs(str(TRASH.absolute()), exist_ok=True)

    extra_message = "" if check_all_usual_paths(files) else "\n\nWARNING: at least one of the selected paths are not in a regular user directory"
    if not confirm(f"Are you sure you want to compress the following files to {TRASH}?{extra_message}\n\n{', '.join(files)}"):
        return

    for file in files:
        file = Path(file)
        if not file.is_dir():
            output_name = file.name
        else:
            output_name = file.name + ".dir"
        header(f"Archiving {file.name} to {TRASH}/trash/")
        run(f'tar -czvf "{TRASH}/{output_name}.tar.gz" "{file.relative_to(file.parent)}"', file.parent)
        header("Removing original file...")
        if file.is_dir():
            rmtree(file.absolute())
        else:
            remove(file.absolute())

commands = {
    "trashpress": trashpress
}


"""SECTION: command-line interface"""
if __name__ == "__main__":
    # Parse arguments
    parser = ArgumentParser(prog="filecat",
        description=f"A file management CLI for CLI tool popup integrations in the file browser. Designed to integrate with Nemo actions: see {__file__} for an example action")
    parser.add_argument("command", choices=commands.keys())
    parser.add_argument("files", nargs="*")
    parser.add_argument("--trash",
        default=TRASH,
        help="[trashpress], directory to move compressed files to. Defaults to the FILECAT_TRASH env var if defined, otherwise ~/.filecat/trash/")

    args = parser.parse_args()
    
    # Use global var to allow files format for now
    TRASH = Path(args.trash)

    # Pass the file parameters to the command
    try:
        commands[args.command](args.files)
    # If an error occurs during the command,
    # print it in red and require ENTER to continue
    except Exception as e:
        print_red(e)
        input("Press ENTER to close...")
