# PyInstaller

- You must build the artifact on the machine you are targeting.

- Need entry point
  - `yojenkins/__main__.py` - `main()`

- Make sure everything is packaged correctly:
  - [Packaging Check](https://github.com/pyinstaller/pyinstaller/wiki/How-to-Report-Bugs#make-sure-everything-is-packaged-correctly)

- First build
  - `pyinstaller yojenkins/__main__.py --name yojenkins`

- Add items to `.gitignore`
  - `*.spec` - Generates after first build, controls future builds
  - `build/` - Build metadata
  - `dist/` - Final artifacts

- Common Options for `pyinstaller` command
  - `--name` - name of build
  - `--onefile`, `F` - Distribution build as only one executable
  - `--onedir`, `D` - Distribution build as one directory
  - `--add-data` / `--add-binary` - Add additional data or binaries into build (stuff in MANIFEST.in?)
  - `--exclude-module` - Exclude specific modules from build (ie. pytest)
  - `--clean` - Remove old builds
  - `-y` - Omit user input

- Debugging
  - `build/<PROJECT>/warn-<PROJECT>.txt` - Warnings
  - Using `--onedir` (default) will allow you to debug output of build closer
  - `--log-level=DEBUG` - Detailed logging output
    - Save to file: `pyinstaller --log-level=DEBUG <PROJECT>.py 2> build_log.txt`

- Command
  - Will create the `.spec` file: `pyinstaller .\yojenkins\__main__.py --name yojenkins --hidden-import "site.getusersitepackages" -y --clean`
  - Using existing `.spec` file: `pyinstaller yojenkins-onefile.spec  -y --clean`
