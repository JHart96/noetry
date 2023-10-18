# Noetry

A minimalist virtual environment and dependency manager for Python.

**Why Noetry?** In the vast universe of Python packaging, `noetry` aims to simplify dependency management and virtual environment handling without the overhead of advanced tools. Poetry is a wonderful tool, but if you want something simpler that just works (sometimes), give `noetry` a shot!

## Features

- **Virtual Environment Management**: Easily create and delete virtual environments.
- **Python Version Management**: Set your Python version without any confusion.
- **Dependency Management**: Use the classic `requirements.txt` approach, simplifying your workflow.
- **Poetry Project Conversion**: Convert your Poetry project to a Noetry one with a single command.

## Installation

Install noetry directly from github:

```bash
pip install git+https://github.com/JHart96/noetry.git

```

## Usage

Get started with the following commands:

- Initialize a Noetry project: `noetry init`
- Create a new virtual environment: `noetry create`
- Delete the virtual environment: `noetry delete`
- Add a package: `noetry add <pkg>`
- Remove a package: `noetry remove <pkg>`
- Set Python version: `noetry set-python <version>`
- List all packages: `noetry list`
- Convert a Poetry project: `noetry convert`
- Run a command in the virtual environment: `noetry run <cmd>`

For more details, run `noetry` without arguments to see the help text.

## Contributing

We welcome contributions! If you find a bug or have a feature request, please open an issue. If you'd like to contribute code, please fork the repository, make your changes, and submit a pull request.

## License

[MIT License](LICENSE)