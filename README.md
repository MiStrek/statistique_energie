# statistique_energie

Project to simulate the electricity prices for the LMD graduate
## Installation

1. As a Python development environment we recommend Pycharm Community for
   Windows: https://www.jetbrains.com/pycharm/download/#section=windows
1. For Pycharm to run and inspect the Python code you need to install Python. We recommend latest Python 3.10 for Windows:
   `Windows installer (64-bit)` https://www.python.org/downloads/
    - Installation interface:
        - Pick custom installation
        - You may need to disable the "py launcher" update option which causes an error
        - We recommend to change the installation path to your D drive to avoid network/random Windows tantrum/McAfee issues.
          For example in: `D:\app\Python\Python39`
    - Add the installation folders in your account's `PATH` environment variable (this is how command line
      interpreters know where the command executables are). For example, I have  
      both `D:\app\Python\Python39` (for `python.exe`)  
      and `D:\app\Python\Python39\Scripts\` (for all global scripts like `pip`) in mine.
    - Testing the install:
        - Make sure `python --version` returns the version you just installed
        - Make sure `which python` (or `where python` in CMD) is pointing to the path you just installed.
    - **Warning**: because of a bug with Git Bash, running the Python interactive interpreter with `python` will not
      work, use `python -i` instead, or better, use [ipython](#ipython).
1. To start contributing to the Python project you'll need to install Git,
   see: [Git installation and workflow](git_and_workflow.md)
   Command lines below are written for Git Bash.


Update to new Python version:
1. Install the new version in a new folder as described above with the Windows installer.
1. Edit the python folder path in your `PATH` environment variable to point to the new installation folder.


## pip

To manage project dependencies (external libraries or packages), you'll need to install the standard Python package
manager `pip`. For installation see: https://pip.pypa.io/en/stable/installing/

To update `pip`:

```shell
python -m pip install --upgrade pip
```

## virtualenv

Dependencies may vary between projects, they may even be incompatible, so it's not recommended installing dependencies
system wide. Instead, we isolate the dependencies of different projects into "virtual environments" using 
`venv` which is included in the Python3 install.

### Create virtualenv

`python -m venv -p path/to/python path/to/virtualenv_directory`

```shell
# If python is in the PATH and you want to store the virtualenv in a project root directory called "venv": 
python -m venv venv
```

### Remove virtualenv

There's nothing else to do than removing the created directory:

```shell
rm -rf venv
```

### Activate or enter virtualenv

We're not using the virtualenv yet! We need to activate it.

Activate, or "enter" the virtual environment so the dependencies installed are isolated from the global system:

```shell
source venv/Scripts/activate
```

The shell prompt should now show the name of the virtualenv folder between parentheses. 
