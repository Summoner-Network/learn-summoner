# From One Agent to Many: An Intro to Summoner

## Installation

### POSIX (Bash)

First installation:

```bash
source build_sdk.sh setup --server python && bash install_requirements.sh
# or if rustup installed:
source build_sdk.sh setup && bash install_requirements.sh
```

Reset:

```bash
source build_sdk.sh reset --server python && bash install_requirements.sh
# or if rustup installed:
source build_sdk.sh reset && bash install_requirements.sh
```

If `source build_sdk.sh reset/setup` does not work, use:
```bash
bash build_sdk.sh reset/setup
source venv/bin/activate
```


### Windows (PowerShell)

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\build_sdk_on_windows.ps1 setup
.\install_requirements_on_windows.ps1
```

## Commands by example

### Template

```
python learn/
```
