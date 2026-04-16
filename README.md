# Filecat
A peculiar CLI to combine terminal tools & graphical file browsers

## How-to
### Requirements:
- *python* (3.9 or newer)
- *git* or *curl*, depending on your installation method
- `[trashpress]`: *tar*
- `[checksum, samesies]`: a checksum cli tool. By default, *sha512sum* is used


### CLI usage
```sh
# Download filecat.py
curl -O https://raw.githubusercontent.com/Denperidge/filecat/refs/heads/main/filecat.py

# Show help
python filecat.py --help

# Compress & move to trash (~/.filecat/trash/)
python filecat.py trashpress file1.png file2.txt

# Return list of checksums for all passed files
python filecat.py checksum file1.png directory/

# Check if contents/checksums are identical
python filecat.py samesies file1.txt file2.txt
```

### Nemo usage
```sh
# From repository root
git clone https://github.com/Denperidge/filecat.git
cd filecat
# Create symbolic links from src/ to the nemo actions directory
ln -s $(pwd)/filecat.py ~/.local/share/nemo/actions/
ln -s $(pwd)/nemo_actions/* ~/.local/share/nemo/actions/
```
Done! Further configuration can be done inside Nemo > Edit > Preferences > Plugins, or by changing the files within [src/](src/)

### Run tests
```sh
echo yyyn\n | python tests/test.py
```

## Explanation
### For who?
If you like graphical file browsers in terms of UX/UI whilst preferring the clarity & transparency of terminals + command line tools, this might be a setup you enjoy!

### What?
1. Filecat contains peculiar commands (for example: compress & move to trash using tar, move file/dir using rsync & checksum) and the boilerplate to write them quicker. These can be found in [filecat.py](src/filecat.py)
2. Filecat is designed to perfectly integrate into the [Nemo filebrowser](https://github.com/linuxmint/nemo) and its actions system. These files can be seen in any *.nemo_action file in [src/](src/)

In my setup, it is used in combination with an [alacritty helper script & niri setup](https://github.com/Denperidge/scripts/blob/345029aa02829fc5a35fbd23fced48449c47b30f/shell-utils/alacritty-run) to create floating terminal popups, but any terminal setup can be used

## License
This project is licensed under the [MIT License](LICENSE).
