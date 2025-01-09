<div align="center">
    <img src=".github/music_harvester.png" width="100">
    <h1>PYTMDL 🎧</h1>
    <h5>PYTMDL is a tool that downloads songs and their corresponding covers from YouTube Music, and then embeds the metadata from iTunes into the songs.</h5>

[![Made with Python](https://img.shields.io/badge/Made%20with-Python-507dbc?style=flat&logo=python&labelColor=aed9e0)](https://python.org "Python")
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=flat)](LICENSE "License")
</div>

## Usage

Clone the repository:
```sh
git clone https://github.com/OpenSourceCatalyst/pytmdl.git
```

`cd` into pytmdl:
```sh
cd pytmdl
```

Install the required dependencies:
```sh
pip install -r requirements.txt
```

Run:
```sh
python main.py [-h] [-v] [-s] [-o OUTPUT] [-l LANGUAGE] [url ...]
```

## Example:

```sh
python main.py -o "~/Desktop" "<song/playlist URL here>"
```

<br>

## Executable

You can create an executable by using the following command:
```sh
pyinstaller --add-data "translations:translations" main.py
```

It will be created by default in `./dist/main/main` in Linux/Mac or `.\dist\main\main.exe` in Windows.

##### Note: adding the `--onefile` argument to pyinstaller tends to make running the executable very slow.