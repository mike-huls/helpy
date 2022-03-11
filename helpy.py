import os
import shutil
import sys
import subprocess
import importlib.util
import urllib.request
import pip
VENVPY = "venv/scripts/python.exe"
PROJECT_DIR = os.path.dirname(__file__)

# region HELPY
def update(verbose: bool = False, force: bool = False):
    """ Downloads new helpy """

    printout(func=update.__name__, msg='updating helpy..', doPrint=verbose)

    REMOTE_URL = "https://raw.githubusercontent.com/mike-huls/helpy/main/helpy.py"
    NAME_MAIN_STRING = 'if __name__ == "__main__":'

    # 1. Get content current file from "__name__ == __main__"
    with open(__file__, 'r') as rfile:
        curfile_lines = rfile.read().split("\n")
    curfile_idx_namemainline = curfile_lines.index(NAME_MAIN_STRING)
    curfile_idx_dateline = curfile_idx_namemainline - 1
    curfile_date = curfile_lines[curfile_idx_dateline]
    curfile_initmain = "\n".join(curfile_lines[curfile_idx_namemainline:])

    # 2. Get new content
    remote_lines = getrequest(url=REMOTE_URL).split("\n")
    remote_idx_initmainline = remote_lines.index(NAME_MAIN_STRING)
    remote_idx_dateline = remote_idx_initmainline - 1
    remote_date = remote_lines[remote_idx_dateline]
    remote_content = "\n".join(remote_lines[:remote_idx_initmainline])

    # 3. If we don't force: compare. Are we up to date?
    if (not force):
        helpy_up_to_date = curfile_date == remote_date
        if (helpy_up_to_date):
            if (verbose):
                printout(func=update.__name__, msg="Helpy is up to date", doPrint=True)
            return
        else:
            if (input("Update available! Update? (y/n)").lower() != 'y'):
                printout(func=update.__name__, msg="Skipping helpy update..", doPrint=True)
                return

    # 3. Combine and write
    newHelpy = remote_content + "\n" + curfile_initmain
    with open(__file__, 'w') as file:
        file.write(newHelpy)

    # Feedback
    remote_idx_dateline = remote_idx_initmainline - 1
    printout(func=update.__name__, msg=f"updated helpy to {remote_lines[remote_idx_dateline].replace('# ', '')}", doPrint=True)
def helpy_cur_version():
    NAME_MAIN_STRING = 'if __name__ == "__main__":'
    with open(__file__, 'r') as rfile:
        curfile_lines = rfile.read().split("\n")
    curfile_idx_namemainline = curfile_lines.index(NAME_MAIN_STRING)
    curfile_idx_dateline = curfile_idx_namemainline - 1
    curfile_date = curfile_lines[curfile_idx_dateline]
    curfile_date = curfile_date.replace("# ", "")
    return curfile_date
def display_info():
    helpy_version = helpy_cur_version()
    printout(func="info", msg=f"""
    HELPY version {helpy_version}
        PYPI:
        PYPI URL: \t {PYPI_URL if (PYPI_URL) else ""}
        PYPI username: \t {PYPI_USERNAME if (PYPI_USERNAME) else ""}
        PYPI password: \t {"*" * len(PYPI_PASSWORD) if (PYPI_PASSWORD) else ""}

        DOCKER:
        image name: \t {DOCKER_IMAGE_NAME if (DOCKER_IMAGE_NAME) else ""}
    """, doPrint=True)
def help():
    helpmessage = f"""
    Welcome to Helpy (v.{helpy_cur_version()})
    Call [python helpy.py] with any of the following commands:
        help                            display this message
        info                            displays information about helpy, including constants you've set
        version                         displays information about the current version of helpy 
        update                          updates helpy if there is a new version
        init project                    prepares the current folder for a python project
        init package                    prepares the current folder for a python package
        freeze                          pip freeze to create requirements.txt
        serve fastapi                   tries to spin up the current project as a fastapi project 
        docker build                    builds the image specified in the dockerfile
        docker push                     pushes the image to dockerhub. Set username in .env or from cmd
        package build                   uses the setup.py to build the package
        package push                    pushes the package to the pypi specified in the .env
        pip install [packagename]       installs a package using pypi OR the pypi specified in helpy (PYPI_URL)
        pip install requirements.txt    installs a requirements.txt file using pypi OR the pypi specified in the helpy (PYPI_URL)
        pip freeze                      freezes all dependencies in a requirements.txt
    Add the -v flag for verbose output
    Add the -y or -f flag to confirm all dialogs"""
    printout(func="help", msg=helpmessage, doPrint=True)
# endregion

# region UTIL
def pop_arg_or_exit(arglist: [str], errormessage: str):
    """ Tries to pop an arg from the list. If this is not possible: display errormessage and exit """
    if (len(arglist) <= 0):
        printout(func="helpy", msg=f"{errormessage}", doPrint=True)
        sys.exit(0)
    return arglist.pop(0).lower()
def getrequest(url: str) -> str:
    httprequest = urllib.request.Request(url, data={}, headers={}, method="GET")
    with urllib.request.urlopen(httprequest) as httpresponse:
        if (httpresponse.status != 200):
            raise ValueError("Error in request, status code not 200")
        return httpresponse.read().decode(httpresponse.headers.get_content_charset("utf-8"))
def printout(msg: str, func: str = None, doPrint: bool = True):
    buffer = 20 - (0 if (func == None) else len(func))
    if (buffer <= 1):
        buffer = 1

    if (doPrint):
        func_str = "" if (func == None) else f"{func}"
        print(f"[Helpy] {func_str}{' ' * buffer}{msg} ")
def create_folder(folderpath: str, verbose: bool = False):
    if (os.path.exists(folderpath)):
        printout(func=create_folder.__name__, msg=f"Folder {folderpath} already exists. Skipping..", doPrint=verbose)
        return
    os.mkdir(path=folderpath)
    printout(func=create_folder.__name__, msg=f"Folder {folderpath} created", doPrint=verbose)
def remove_folder(folderpath: str, verbose: bool = False):
    if (os.path.isdir(folderpath)):
        shutil.rmtree(folderpath)
    printout(func=remove_folder.__name__, msg=f"Folder {folderpath} removed", doPrint=verbose)
def download_file(url: str, filepath: str, verbose: bool = False, overwrite: bool = False):
    """ download a file from a url to the given file path """

    if (not overwrite):
        if (os.path.isfile(filepath)):
            printout(func=download_file.__name__, msg=f"File {filepath} already exists. Skipping..", doPrint=verbose)
            return
    with open(filepath, 'w') as file:
        file.write(getrequest(url=url))
def create_empty_file(filepath: str, verbose: bool = False, overwrite: bool = False):
    """ Creates an empty file if not exists """

    if (not overwrite):
        if (os.path.isfile(filepath)):
            printout(func=create_empty_file.__name__, msg=f"File {filepath} already exists. Skipping..", doPrint=verbose)
            return
    with open(filepath, 'w') as file:
        file.write("")
def replace_in_file(filepath: str, replace_this_text: str, replacment_text: str):
    """ Replaces a text with the replacement text in a text file """
    with open(filepath, 'r') as file:
        filedata = file.read()

    # Replace the target string
    filedata = filedata.replace(replace_this_text, replacment_text)

    # Write the file out again
    with open(filepath, 'w') as file:
        file.write(filedata)
# endregion

# region ENV
def load_env_vars(env_file_path: str = None, verbose:bool=False) -> None:
    install_package(package_name='python-dotenv', prompt_sure=True, verbose=verbose)
    # try:
    #     from dotenv import load_dotenv
    # except ImportError as e:
    #     subprocess.call(f"{VENVPY} -m pip install python-dotenv --upgrade")
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=env_file_path)
def venv_exists() -> bool:
    return os.path.isfile(VENVPY)
def create_virtualenv(projectfolder: str, verbose: bool = False):
    """ Creates a virtual environment in a project folder """

    if (os.path.exists(os.path.join(projectfolder, 'venv'))):
        printout(func=create_virtualenv.__name__, msg=f"Virtual environment already exists", doPrint=verbose)
        return

    # try:
    #     import venv
    # except ImportError as e:
    #     printout(func=create_virtualenv.__name__, msg=f"Create venv: venv not installed: installing..", doPrint=verbose)
    #     subprocess.call(f"{VENVPY} -m pip install venv --upgrade")
    #     printout(func=create_virtualenv.__name__, msg=f"Create venv: venv successfully installed.", doPrint=verbose)
    install_package_globally(package_name='virtualenv', import_package_name='venv', prompt_sure=True, verbose=verbose)
    printout(func=create_virtualenv.__name__, msg=f"Installing virtualenv", doPrint=verbose)
    subprocess.call(f'python.exe -m venv {projectfolder}/venv')
    printout(func=create_virtualenv.__name__, msg=f"Successfully created virtualenv", doPrint=verbose)


# endregion

# region INIT
def init_project(verbose: bool = False, force: bool = False, project_name:str="My Project"):
    """ Needs certain files and folder structure always. """

    PROJFOLDER = os.getcwd()
    printout(func=init_project.__name__, msg=f"Initializing new project '{project_name}' at {PROJFOLDER}..", doPrint=verbose)
    FILES_URL = f"https://raw.githubusercontent.com/mike-huls/helpy/main/files"

    # Create venv
    printout(func=init_project.__name__, msg=f"Initializing venv..", doPrint=verbose)
    create_virtualenv(projectfolder=PROJFOLDER, verbose=verbose)
    printout(func=init_project.__name__, msg=f"Initialized venv", doPrint=verbose)

    # config/conf/.env
    printout(func=init_project.__name__, msg=f"Creating default folders and files..", doPrint=verbose)
    create_folder(folderpath=os.path.join(PROJFOLDER, 'config'), verbose=verbose)
    create_folder(folderpath=os.path.join(PROJFOLDER, 'config', 'conf'), verbose=verbose)
    download_file(url=f"{FILES_URL}/default_env", filepath=os.path.join(PROJFOLDER, 'config', 'conf', '.env'), verbose=verbose, overwrite=force)

    # default folders
    create_folder(folderpath=os.path.join(PROJFOLDER, 'services'), verbose=verbose)

    # Create default files (with content)
    download_file(url=f"{FILES_URL}/default_dockerignore", filepath=os.path.join(PROJFOLDER, '.dockerignore'), verbose=verbose, overwrite=force)
    download_file(url=f"{FILES_URL}/default_main.py", filepath=os.path.join(PROJFOLDER, 'main.py'), verbose=verbose, overwrite=force)
    download_file(url=f"{FILES_URL}/default_gitignore", filepath=os.path.join(PROJFOLDER, '.gitignore'), verbose=verbose, overwrite=force)
    download_file(url=f"{FILES_URL}/default_readme_project.md", filepath=os.path.join(PROJFOLDER, 'readme.md'), verbose=verbose, overwrite=force)

    replace_in_file(filepath=os.path.join(PROJFOLDER, 'readme.md'), replace_this_text='{PROJECT_NAME}', replacment_text=project_name)
    download_file(url=f"{FILES_URL}/default_Dockerfile", filepath=os.path.join(PROJFOLDER, 'Dockerfile'), verbose=verbose, overwrite=force)

    printout(func=init_project.__name__, msg=f"Project initialized", doPrint=True)


def init_package(package_name: str, verbose: bool = False, force: bool = False):
    """ Get files and folder structure"""
    PROJFOLDER = os.getcwd()
    printout(func=init_project.__name__, msg=f"Initializing new project at {PROJFOLDER}..", doPrint=verbose)
    FILES_URL = f"https://raw.githubusercontent.com/mike-huls/helpy/main/files"

    # Create venv
    printout(func=init_project.__name__, msg=f"Initializing venv..", doPrint=verbose)
    create_virtualenv(projectfolder=PROJFOLDER, verbose=verbose)
    printout(func=init_project.__name__, msg=f"Initialized venv", doPrint=verbose)

    printout(func=init_project.__name__, msg=f"Creating default folders and files..", doPrint=verbose)
    # Create module folder with __init__.py
    create_folder(folderpath=os.path.join(PROJFOLDER, package_name), verbose=verbose)
    create_empty_file(filepath=os.path.join(PROJFOLDER, package_name, '__init__.py'), verbose=verbose)

    # config/conf/.env
    create_folder(folderpath=os.path.join(PROJFOLDER, 'config'), verbose=verbose)
    create_folder(folderpath=os.path.join(PROJFOLDER, 'config', 'conf'), verbose=verbose)
    download_file(url=f"{FILES_URL}/default_env", filepath=os.path.join(PROJFOLDER, 'config', 'conf', '.env'), verbose=verbose, overwrite=force)
    create_empty_file(filepath=os.path.join(PROJFOLDER, 'config', 'conf', '.env'), verbose=verbose, overwrite=force)

    # Create default files (with content)
    download_file(url=f"{FILES_URL}/default_dockerignore", filepath=os.path.join(PROJFOLDER, '.dockerignore'), verbose=verbose, overwrite=force)
    download_file(url=f"{FILES_URL}/default_gitignore", filepath=os.path.join(PROJFOLDER, '.gitignore'), verbose=verbose, overwrite=force)
    download_file(url=f"{FILES_URL}/default_readme_package.md", filepath=os.path.join(PROJFOLDER, 'readme.md'), verbose=verbose, overwrite=force)
    replace_in_file(filepath=os.path.join(PROJFOLDER, 'readme.md'), replace_this_text='{PROJECT_NAME}', replacment_text=package_name)
    download_file(url=f"{FILES_URL}/default_setup.cfg", filepath=os.path.join(PROJFOLDER, 'setup.cfg'), verbose=verbose, overwrite=force)
    download_file(url=f"{FILES_URL}/default_setup.py", filepath=os.path.join(PROJFOLDER, 'setup.py'), verbose=verbose, overwrite=force)
    replace_in_file(filepath=os.path.join(PROJFOLDER, 'setup.py'), replace_this_text='{PROJECT_NAME}', replacment_text=package_name)


    printout(func=init_project.__name__, msg=f"Project initialized", doPrint=True)


# endregion

# region SERVE
def serve_fastapi(verbose:bool=False):
    """ Makes it so that you can serve fastapi"""

    # 1. Ensure Fastapi is installed
    ensure_package_installed(package_name='fastapi', show_prompt=True)
    # try:
    #     import fastapi
    #     printout(func=serve_fastapi.__name__, msg="fastpi not installed; installing..", doPrint=verbose)
    # except ImportError as e:
    #     subprocess.call("venv/scripts/python.exe -m pip install fastapi --upgrade")
    #     printout(func=serve_fastapi.__name__, msg="Installed fastapi", doPrint=verbose)

    # 2. Ensure uvicorn is installed
    ensure_package_installed(package_name='uvicorn', show_prompt=True)
    # try:
    #     import uvicorn
    #     printout(func=serve_fastapi.__name__, msg="uvicorn not installed; installing..", doPrint=verbose)
    # except ImportError as e:
    #     subprocess.call("venv/scripts/python.exe -m pip install uvicorn --upgrade")
    #     printout(func=serve_fastapi.__name__, msg="Installed uvicorn", doPrint=verbose)

    # 3. Serve fastapi on uvicorn
    try:
        subprocess.call('venv/scripts/python.exe -m uvicorn main:app --env-file config/conf/.env --reload')
    except Exception as e:
        printout(func=serve_fastapi.__name__, msg=f"Serving project with FastAPI failed: \n\t'{e}'", doPrint=True)
# endregion

# region DOCKER
def docker_system_prune():
    try:
        subprocess.call(f"docker system prune -f")
    except Exception as e:
        printout(func=docker_system_prune.__name__, msg=f"Docker system prune failed: \t\n'{e}'", doPrint=True)


def docker_login(docker_username: str, docker_password: str, verbose: bool = False):
    """ Use the docker image name to log in """


def docker_build(verbose: bool = False):
    if (len(DOCKER_IMAGE_NAME) < 3):
        printout(func=docker_build.__name__, msg="Please provide a docker image name in helpy.py", doPrint=True)
        return
    printout(func=docker_build.__name__, msg=f"Building docker image '{DOCKER_IMAGE_NAME}'..", doPrint=verbose)
    pip_freeze(verbose=verbose)
    try:
        subprocess.call(f'docker build . -t "{DOCKER_IMAGE_NAME}" --secret id=pypicreds,src=config\conf\.env')
        docker_system_prune()
        printout(func=docker_build.__name__, msg=f"Successfully built docker image", doPrint=verbose)
    except Exception as e:
        printout(func=docker_build.__name__, msg=f"Failed to build docker image: \n\t'{e}", doPrint=True)


def docker_push(verbose: bool = False, force: bool = False):
    """ Pushes the docker image to the docker hub """

    if (len(DOCKER_IMAGE_NAME) <= 3):
        printout(func=docker_push.__name__, msg=f"Invalid DOCKER_IMAGE_NAME: '{DOCKER_IMAGE_NAME}'. Please provide a docker image name in helpy.py", doPrint=True)
        return

    if (not force):
        if (input(f"Are you sure you want to push '{DOCKER_IMAGE_NAME}' to dockerhub? (y/n)").lower() != "y"):
            return

    printout(func=docker_push.__name__, msg=f"Pushing image '{DOCKER_IMAGE_NAME}' to docker hub", doPrint=verbose)
    try:
        subprocess.call(f'docker push "{DOCKER_IMAGE_NAME}"')
        printout(func=docker_push.__name__, msg=f"Successfully pushed image '{DOCKER_IMAGE_NAME}' to docker hub", doPrint=verbose)
    except Exception as e:
        printout(func=docker_push.__name__, msg=f"Failed to push docker image: \n\t'{e}'", doPrint=True)


# endregion

# region PYPI - PACKAGES
def package_build(verbose: bool = False):
    """ packages code in current directory to the dist folder """

    dist_folder_path = os.path.join(os.getcwd(), 'dist')
    if (os.path.isdir(dist_folder_path)):
        printout(func=package_build.__name__, msg=f"removing content of dist folder at {dist_folder_path}", doPrint=verbose)
        remove_folder(folderpath=dist_folder_path, verbose=False)
        create_folder(folderpath=dist_folder_path, verbose=False)
        printout(func=package_build.__name__, msg=f"removed content of dist folder at {dist_folder_path}", doPrint=verbose)
    else:
        printout(func=package_build.__name__, msg=f"Dist folder does not exist yet. Skipping..", doPrint=verbose)

    pip_freeze(verbose=verbose)
    # try:
    #     import twine
    # except ImportError as e:
    #     subprocess.call("venv/scripts/python.exe -m pip install twine --upgrade")
    ensure_package_installed(package_name='twine', show_prompt=True)

    subprocess.call(f"{VENVPY} setup.py sdist")
def package_push(pypi_url: str, pypi_username: str, pypi_password: str, verbose: bool = False, force: bool = False):
    """ Pushes the package to pypi server """

    if (not force):
        if (input("Are you sure you want to push the package to PyPi? (y/n)").lower() != 'y'):
            return

    # 2. Ensure twine is installed
    ensure_package_installed(package_name='twine', show_prompt=True)
    # try:
    #     import twine
    # except ImportError as e:
    #     printout(func=package_push.__name__, msg="twine not installed; installing..", doPrint=verbose)
    #     subprocess.call("venv/scripts/python.exe -m pip install twine --upgrade")
    #     printout(func=package_push.__name__, msg="Successfully installed twine", doPrint=verbose)

    # 3. Call package push
    printout(func=package_push.__name__, msg=f"Pushing package to '{pypi_url}'", doPrint=verbose)
    try:
        subprocess.call(f'{VENVPY} -m twine upload dist/* --repository-url "{pypi_url}" -u "{pypi_username}" -p "{pypi_password}"')
        printout(func=package_push.__name__, msg=f"Successfully pushed package to '{pypi_url}'", doPrint=verbose)
    except Exception as e:
        printout(func=package_push.__name__, msg=f"Failed push package to '{pypi_url}': \n\t'{e}'", doPrint=True)
# endregion

# region PIP
def pip_freeze(verbose: bool = False):
    printout(func=pip_freeze.__name__, msg=f"Pip freezing requirements..", doPrint=verbose)
    try:
        python_location = os.path.join(os.getcwd(), VENVPY)
        with open('requirements.txt', 'w') as file_:
            subprocess.call([python_location, '-m', 'pip', 'freeze'], stdout=file_)
        printout(func=pip_freeze.__name__, msg=f"Pip freeze requirements succes", doPrint=verbose)
    except Exception as e:
        printout(func=pip_freeze.__name__, msg=f"Pip freeze failed: \n\t'{e}'", doPrint=True)
def pip_install_package(pypi_url:str, pypi_username:str, pypi_pasword:str, package_name:str, verbose:bool=False):
    """ Installs a package using your custom pypi url that you specified in the settings of helpy """

    printout(func=f"{pip_install_package.__name__}", msg=f"Installing package {package_name}", doPrint=verbose)
    pypi_url_split = pypi_url.split("://")[1]
    cmd = f"{VENVPY} -m pip install --extra-index-url https://{pypi_username}:{pypi_pasword}@{pypi_url_split} {package_name} --upgrade"
    subprocess.call(cmd)
    printout(func=f"{pip_install_package.__name__}", msg=f"Installed {package_name}", doPrint=verbose)
def install_requirementstxt(pypi_url:str, pypi_username:str, pypi_pasword:str, verbose:bool=False):
    """ Installs all packages in the requirements.txt file """

    printout(func=f"{pip_install_package.__name__}", msg=f"Installing requirements.txt", doPrint=verbose)
    pypi_url_split = pypi_url.split("://")[1]
    cmd = f"{VENVPY} -m pip install --extra-index-url https://{pypi_username}:{pypi_pasword}@{pypi_url_split} -r requirements.txt --upgrade"
    subprocess.call(cmd)
    printout(func=f"{pip_install_package.__name__}", msg=f"Installed requirements.txt", doPrint=verbose)


def package_is_installed(package_name:str) -> bool:
    """ Returns t/f depending on whether a package is installed in this project
        :arg package_name   str     name of the package you're checking
    """
    return importlib.util.find_spec(package_name) != None
def pip_list() -> None:
    cmd:str = f"pip list"
    p = subprocess.Popen(['pip', 'list'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, err = p.communicate(b"input data that is passed to subprocess' stdin")
    rc = p.returncode
    print(output, err, rc)
def install_package_globally(package_name:str, import_package_name:str=None, prompt_sure:bool=False, verbose:bool=False, force:bool=False) -> None:
    """ Installs a package globally, NOT in the project venv """
    # Check if already installed

    # Check if we need to ask for confirmation
    if (prompt_sure):
        if (input(f"Are you sure you want to install package '{package_name}'? (y/n)").lower().strip() != 'y'):
            printout(func=install_package_globally.__name__, msg=f"Exiting..", doPrint=verbose)
            return

    # Check if the package is already installed
    if (not force):
        already_installed = package_is_installed(package_name=package_name)
        if (import_package_name != None):
            # Check alternative name (virtualenv has an importname of venv e.g.)
            if (package_is_installed(package_name=import_package_name)):
                already_installed = True
        if (already_installed):
            printout(func=install_package_globally.__name__, msg=f"Package {package_name} already installed. Skipping..", doPrint=verbose)
            return

    # Install
    printout(func=install_package_globally.__name__, msg=f"Installing {package_name}..", doPrint=verbose)
    cmd:str = f"pip install {package_name} --upgrade"
    res = subprocess.call(cmd)
    printout(func=install_package_globally.__name__, msg=f"Installed {package_name}", doPrint=verbose)
def install_package(package_name:str, import_package_name:str=None, python_location:str="venv/Scripts/python.exe", prompt_sure:bool=False, verbose:bool=False, force:bool=False) -> None:
    """ Calls pip module using the python location to install the package name"""
    printout(func=install_package.__name__, msg=f"Installing {package_name}..", doPrint=verbose)

    if (prompt_sure):
        if (input(f"Install package {package_name}? (y/n)").lower().strip() != 'y'):
            printout(func=install_package.__name__, msg=f"Exiting..", doPrint=verbose)

    # Check if the package is already installed
    if (not force):
        already_installed = package_is_installed(package_name=package_name)
        if (import_package_name != None):
            # Check alternative name (virtualenv has an importname of venv e.g.)
            if (package_is_installed(package_name=import_package_name)):
                already_installed = True
        if (already_installed):
            printout(func=install_package_globally.__name__, msg=f"Package {package_name} already installed. Skipping..", doPrint=verbose)
            return

    cmd:str = f"{python_location} -m pip install {package_name} --upgrade"
    res = subprocess.call(cmd)
    printout(func=install_package.__name__, msg=f"Installed {package_name}", doPrint=verbose)
# endregion


def main():
    """ Parse command line """
    args = sys.argv[1:]


    if (len(args) == 0):
        help()
        quit()
    cmd1 = pop_arg_or_exit(arglist=args, errormessage="Helpy expects at least one argument. Check out [helpy.py help] for more information")

    # Settings
    DO_FORCE = len({'f', 'y'} & set(["".join(a.split("-")) for a in args])) > 0
    VERBOSE = len({'v'} & set(["".join(a.split("-")) for a in args])) > 0
    args = [a for a in args if (a[0] != '-')]

    # Check for updates
    if (cmd1 != 'update'):
        # Checks for updates
        update(force=False, verbose=VERBOSE)

    # Regular functions
    if (cmd1 == 'update'):
        #
        update(force=True, verbose=VERBOSE)
    elif (cmd1 == 'help'):
        #
        help()
    elif (cmd1 == 'info'):
        #
        display_info()
    elif (cmd1 == 'version'):
        #
        print(f"Helpy version {helpy_cur_version()}")
    elif (cmd1 == 'init'):
        # Get init_type
        init_type = pop_arg_or_exit(arglist=args, errormessage="[helpy.py init] requires another argument. Check out [helpy.py help] for more information")

        # Functions
        if (init_type == 'project'):
            project_name = args[0] if (len(args) > 0) else None
            if (project_name == None):
                project_name = input("Project name?")
            init_project(force=DO_FORCE, verbose=VERBOSE, project_name=project_name)
        elif (init_type == 'package'):
            package_name = args[0] if (len(args) > 0) else None
            if (package_name == None):
                package_name = input("What is this package called?")
            init_package(package_name=package_name, verbose=VERBOSE, force=DO_FORCE)
        else:
            printout(func="helpy", msg=f"Unknown option for helpy init: '{init_type}'. Check out [helpy.py help] for more information")
    elif (cmd1 == 'serve'):
        # Get application type
        available_apps = ['fastapi']
        serve_op = pop_arg_or_exit(
            arglist=args,
            errormessage="[helpy.py serve] requires another argument. Example: [helpy.py serve <apptype>]. "
                         "Check out a list of available apps at [helpy.py serve list]")
        if (serve_op == 'list'):
            printout(func="helpy", msg=f"Available apps: {available_apps} \t\t Example: [helpy.py serve {available_apps[0]}]")
        elif (serve_op == 'fastapi'):
            serve_fastapi()
        else:
            printout(func="helpy", msg=f"Unknown option for [helpy.py serve]: '{serve_op}'. Check out [helpy.py serve list] for more information")
    elif (cmd1 == 'docker'):
        docker_op = pop_arg_or_exit(arglist=args, errormessage="[helpy.py docker] requires another argument. Check out [helpy.py help] for more information")

        if (docker_op == 'build'):
            docker_build(verbose=VERBOSE)
        elif (docker_op == 'push'):
            docker_push(force=DO_FORCE, verbose=VERBOSE)
        else:
            printout(func="helpy", msg=f"Unknown option for [helpy.py docker]: '{docker_op}'. Check out [helpy.py help] for more information")
    elif (cmd1 == 'package'):
        package_op = pop_arg_or_exit(arglist=args, errormessage="[helpy.py package] requires another argument. Check out [helpy.py help] for more information")

        if (package_op == 'build'):
            package_build(verbose=VERBOSE)
        elif (package_op == 'push'):
            # 1. Check if all variables are set
            if (len(str(PYPI_URL)) <= 5):
                printout(func="push", msg="Please set PyPi Url in helpy.py")
                sys.exit(0)
            if (len(str(PYPI_USERNAME)) <= 5):
                printout(func="push", msg="Please set PyPi Username in helpy.py")
                sys.exit(0)
            if (len(str(PYPI_PASSWORD)) <= 5):
                printout(func="push", msg="Please set PyPi Password in helpy.py")
                sys.exit(0)
            package_push(verbose=VERBOSE, force=DO_FORCE, pypi_url=PYPI_URL, pypi_username=PYPI_USERNAME, pypi_password=PYPI_PASSWORD)
        else:
            printout(func="helpy", msg=f"Unknown option for [helpy.py package]: '{package_op}'. Check out [helpy.py help] for more information")
    elif (cmd1 == 'pip'):
        pip_op = pop_arg_or_exit(arglist=args, errormessage="[helpy.py package] requires another argument. Check out [helpy.py help] for more information")
        if (pip_op == 'install'):

            # 1. Check if all required variables are set
            if (len(str(PYPI_URL)) <= 5):
                printout(func="push", msg="Please set PyPi Url in helpy.py")
                sys.exit(0)
            if (len(str(PYPI_USERNAME)) <= 5):
                printout(func="push", msg="Please set PyPi Username in helpy.py")
                sys.exit(0)
            if (len(str(PYPI_PASSWORD)) <= 5):
                printout(func="push", msg="Please set PyPi Password in helpy.py")
                sys.exit(0)

            if ('requirements.txt' in " ".join(args)):
                install_requirementstxt(pypi_url=PYPI_URL, pypi_username=PYPI_USERNAME, pypi_pasword=PYPI_PASSWORD, verbose=VERBOSE, force=DO_FORCE)
            else:
                # 2. Package name should be set or taken from input
                package_name = args[0] if (len(args) > 0) else None
                if (package_name == None):
                    printout(func="tip", msg="you can also provide the package like python helpy.py pip install [packagename]", doPrint=True)
                    package_name = input("Install which package?")
                pip_install_package(pypi_url=PYPI_URL, pypi_username=PYPI_USERNAME, pypi_pasword=PYPI_PASSWORD, package_name=package_name, verbose=VERBOSE, force=DO_FORCE)



        elif (pip_op == 'freeze'):
            pip_freeze(verbose=VERBOSE)
        else:
            printout(func="helpy", msg=f"Unknown option for [helpy.py pip]: '{pip_op}'. Check out [helpy.py help] for more information")
    else:
        print(f"unknown command: '{cmd1}'")
        help()


# 2022-03-09 15:45
if __name__ == "__main__":
    # print("globally")
    # install_package_globally(package_name='virtualenv', import_package_name='venv', prompt_sure=True, verbose='-v' in sys.argv, force='-f' in sys.argv)
    #
    # quit()



    # PYPI
    load_env_vars(env_file_path='config/conf/.env')
    PYPI_URL: str = 'tttttttttttttttt' #None # os.environ.get("PYPI_URL")
    PYPI_USERNAME: str = 'tttttttttttttttt' #None # os.environ.get("PYPI_USER")
    PYPI_PASSWORD: str = 'tttttttttttttttt' #None # os.environ.get("PYPI_PASS")
    # DOCKER
    DOCKER_IMAGE_NAME: str = "docker-hub.mywebsite.com/project/package"

    main()


