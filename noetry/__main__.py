import os
import sys
import subprocess
import venv
import toml
import re


def create_virtualenv(project_dir, python_version="3.10"):
    venv_dir = os.path.join(project_dir, '.venv')

    subprocess.run([f"python{python_version}", "-m", "venv", venv_dir])
    print(f"Created virtual environment at: {venv_dir}")

    print("Installing requirements...")
    install_requirements(project_dir)


def delete_virtualenv(project_dir):
    venv_dir = os.path.join(project_dir, '.venv')
    subprocess.run(['rm', '-rf', venv_dir])
    print(f"Deleted virtual environment at: {venv_dir}")


def install_package(project_dir, package):
    venv_dir = os.path.join(project_dir, '.venv')
    pip_exe = get_pip_exe(venv_dir)
    subprocess.run([pip_exe, 'install', package])

    # Add the package to requirements.txt
    update_requirements(project_dir)

    print(f"Installed package: {package}")


def uninstall_package(project_dir, package):
    venv_dir = os.path.join(project_dir, '.venv')
    pip_exe = get_pip_exe(venv_dir)
    subprocess.run([pip_exe, 'uninstall', '-y', package])

    # Remove the package from requirements.txt
    update_requirements(project_dir)

    print(f"Uninstalled package: {package}")


def run_in_venv(project_dir, *commands):
    venv_dir = os.path.join(project_dir, '.venv')
    if not os.path.exists(venv_dir):
        print("Error: No virtual environment found in this project. Please use 'noetry create'.")
        return

    activate_script = os.path.join(venv_dir, 'bin', 'activate')
    if not os.path.exists(activate_script):
        activate_script = os.path.join(venv_dir, 'Scripts', 'activate')

    if os.name == 'posix':
        cmd = f". {activate_script} && {' '.join(commands)}"
        subprocess.run(cmd, shell=True)
    elif os.name == 'nt':  # Windows
        cmd = f"{activate_script} && {' '.join(commands)}"
        subprocess.run(cmd, shell=True, executable='cmd.exe')
    else:
        print("Error: Unsupported OS.")


def get_pip_exe(venv_dir):
    return os.path.join(venv_dir, 'Scripts', 'pip') if sys.platform == 'win32' else os.path.join(venv_dir, 'bin', 'pip')


def init_project(project_dir):

    # Check if virtual environment already exists
    venv_dir = os.path.join(project_dir, '.venv')
    if os.path.exists(venv_dir):
        print("💥 Error: A virtual environment already exists in this project. If you want to reinitialize the project, please delete the .venv directory first.")
        return

    if not os.path.exists(os.path.join(project_dir, 'requirements.txt')):
        # create requirements.txt
        with open(os.path.join(project_dir, 'requirements.txt'), 'w') as f:
            f.write('')
        print("Created requirements.txt")

    create_virtualenv(project_dir)

    print("🚀 Noetry project initialized successfully!")


def install_requirements(project_dir):
    # Install all packages from requirements.txt
    venv_dir = os.path.join(project_dir, '.venv')
    pip_exe = get_pip_exe(venv_dir)
    subprocess.run([pip_exe, 'install', '-r', 'requirements.txt'])


def update_requirements(project_dir):
    # Write to requirements.txt using pip freeze from the virtual environment
    venv_dir = os.path.join(project_dir, '.venv')
    pip_exe = get_pip_exe(venv_dir)

    # Use subprocess to capture the output of pip freeze
    result = subprocess.run([pip_exe, 'freeze'],
                            capture_output=True, text=True)
    requirements = result.stdout

    # Write the captured output to requirements.txt
    with open(os.path.join(project_dir, 'requirements.txt'), 'w') as f:
        f.write(requirements)


def list_packages(project_dir):
    venv_dir = os.path.join(project_dir, '.venv')
    if not os.path.exists(venv_dir):
        print("Error: No virtual environment found in this project. Please use 'noetry create'.")
        return

    pip_exe = get_pip_exe(venv_dir)
    subprocess.run([pip_exe, 'list'])


def set_python_version(project_dir, version):
    print("Setting Python version to: ", version)

    # Check Python version, capture output, and pattern match with Python x.y.z
    result = subprocess.run(
        [f'python{version}', '-V'], capture_output=True, text=True)

    match = re.search(r'Python (\d+\.\d+\.\d+)', result.stdout)

    if not match:
        print(
            f"💥 Error: Python {version} is not installed on your system. Please install it to continue.")
        return

    # remove the current virtual environment
    delete_virtualenv(project_dir)
    # recreate with the specified Python version
    create_virtualenv(project_dir, version)

    print(f"🚀 Python version successfully set to: {version}")


def get_python_version(project_dir):
    run_in_venv(project_dir, 'python', '--version')


def convert_from_poetry(project_dir):
    poetry_file = os.path.join(project_dir, 'pyproject.toml')

    if not os.path.exists(poetry_file):
        print("Error: pyproject.toml not found in the current directory.")
        return

    with open(poetry_file, 'r') as file:
        poetry_data = toml.load(file)

    # Extracting dependencies and dev-dependencies
    dependencies = poetry_data.get('tool', {}).get(
        'poetry', {}).get('dependencies', {})
    dev_dependencies = poetry_data.get('tool', {}).get(
        'poetry', {}).get('dev-dependencies', {})

    # Removing the python version from dependencies, as it's not a package
    if "python" in dependencies:
        del dependencies["python"]

    # Convert TOML format to requirements.txt format
    requirements = []
    for name, version in {**dependencies, **dev_dependencies}.items():
        if version == "*":
            requirements.append(name)
        elif version.startswith("^"):
            requirements.append(f"{name}>={version[1:]}")
        elif version.startswith("~"):
            requirements.append(f"{name}>={version[1:]},<{version[1:][:-1]}")
        else:
            requirements.append(f"{name}=={version}")

    # Write to requirements.txt
    with open(os.path.join(project_dir, 'requirements.txt'), 'w') as file:
        file.write('\n'.join(requirements))

    # Initialize project
    init_project(project_dir)

    print("🚀 Converted Poetry project to Noetry.")


def main():
    if len(sys.argv) < 2:
        show_help()
        return

    cmd = sys.argv[1]
    args = sys.argv[2:]  # This captures the remaining arguments

    project_dir = os.getcwd()

    if cmd == 'create':
        create_virtualenv(project_dir)
    elif cmd == 'delete':
        delete_virtualenv(project_dir)
    elif cmd == 'add':
        if args:
            install_package(project_dir, args[0])
        else:
            print("Please specify a package to add.")
    elif cmd == 'remove':
        if args:
            uninstall_package(project_dir, args[0])
        else:
            print("Please specify a package to remove.")
    elif cmd == 'set-python':
        if args:
            set_python_version(project_dir, args[0])
        else:
            print("Please specify a Python version.")
    elif cmd == 'get-python':
        get_python_version(project_dir)
    elif cmd == 'init':
        init_project(project_dir)
    elif cmd == 'convert':
        convert_from_poetry(project_dir)
    elif cmd == 'run':
        if args:
            run_in_venv(project_dir, *args)
        else:
            print("Please specify a command to run.")
    elif cmd == 'list':
        list_packages(project_dir)
    else:
        print(f"💥 Unknown command: {cmd}")
        show_help()


def show_help():
    help_text = """
Noetry - A simple virtual environment and dependency manager

Commands:
    init                 - Initialize a new noetry project
    create               - Create a new virtual environment for the project
    delete               - Delete the virtual environment for the project
    add <pkg>            - Install a package and add it to requirements.txt
    remove <pkg>         - Uninstall a package and remove it from requirements.txt
    set-python <version> - Set the Python version for the virtual environment
    get-python           - Get the Python version for the virtual environment
    convert              - Convert a Poetry project to a Noetry project
    run <cmd>            - Run a command within the virtual environment
    list                 - List all packages installed in the virtual environment

Example:
    noetry add requests
    noetry run python script.py
    noetry list
    """

    print(help_text)


if __name__ == '__main__':
    main()
