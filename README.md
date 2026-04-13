# Filecat
A peculiar CLI to combine terminal tools & graphical file browsers

## Explanation
### For who?
If you like graphical file browsers in terms of UX/UI whilst preferring the clarity & transparency of terminals + command line tools, this might be a setup you enjoy!

### What?
1. Filecat contains peculiar commands (for example: compress & move to trash using tar, move file/dir using rsync & checksum) and the boilerplate to write them quicker. These can be found in [filecat.py](src/filecat.py)
2. Filecat is designed to perfectly integrate into the [Nemo filebrowser](https://github.com/linuxmint/nemo) and its actions system. These files can be seen in any *.nemo_action file in [src/](src/)

In my setup, it is used in combination with an [alacritty helper script & niri setup](https://github.com/Denperidge/scripts/blob/345029aa02829fc5a35fbd23fced48449c47b30f/shell-utils/alacritty-run) to create floating terminal popups, but any terminal setup can be used

## How-to
### Requirements:
- Python (3.9 or newer)
- Zenity

### CLI usage
```sh
# Download filecat.py
curl -O https://raw.githubusercontent.com/Denperidge/filecat/refs/heads/main/src/filecat.py

# Show help
python filecat.py --help

# Compress & move to trash
python filecat.py trashpress file1.png file2.txt
```

### Nemo usage
```sh
# From repository root
git clone https://github.com/Denperidge/filecat.git
cd filecat
# Create symbolic links from src/ to the nemo actions directory
ln -s $(pwd)/src/* ~/.local/share/nemo/actions/
```
Done! Further configuration can be done inside Nemo > Edit > Preferences > Plugins, or by changing the files within [src/](src/).

## License
This project is licensed under the [MIT License](LICENSE).
