import os
import sys
import subprocess
import urllib.request

VENVPY = "venv/scripts/python.exe"


# region HELPY
def update(verbose: bool = False, force: bool = False):
    """ Downloads new helpy """

    printout(func=update.__name__, msg='updating helpy..', doPrint=verbose)

    GIST_URL = "https://raw.githubusercontent.com/mike-huls/helpy/main/helpy.py"
    NAME_MAIN_STRING = 'if __name__ == "__main__":'

    # 1. Get content current file from "__name__ == __main__"
    with open(__file__, 'r') as rfile:
        curfile_lines = rfile.read().split("\n")
    curfile_idx_namemainline = curfile_lines.index(NAME_MAIN_STRING)
    curfile_idx_dateline = curfile_idx_namemainline - 1
    curfile_date = curfile_lines[curfile_idx_dateline]
    curfile_initmain = "\n".join(curfile_lines[curfile_idx_namemainline:])

    # 2. Get new content
    gist_lines = getrequest(url=GIST_URL).split("\n")
    gist_idx_initmainline = gist_lines.index(NAME_MAIN_STRING)
    gist_idx_dateline = gist_idx_initmainline - 1
    gist_date = gist_lines[gist_idx_dateline]
    gist_content = "\n".join(gist_lines[:gist_idx_initmainline])

    # 3. If we don't force: compare. Are we up to date?
    if (not force):
        helpy_up_to_date = curfile_date == gist_date
        if (helpy_up_to_date):
            if (verbose):
                printout(func=update.__name__, msg="Helpy is up to date", doPrint=True)
            return
        else:
            if (input("Update available! Update? (y/n)").lower() != 'y'):
                printout(func=update.__name__, msg="Skipping helpy update..", doPrint=True)
                return

    # 3. Combine and write
    newHelpy = gist_content + "\n" + curfile_initmain
    with open(__file__, 'w') as file:
        file.write(newHelpy)

    # Feedback
    gist_idx_dateline = gist_idx_initmainline - 1
    printout(func=update.__name__, msg=f"updated helpy to {gist_lines[gist_idx_dateline].replace('# ', '')}", doPrint=True)


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
        help                        display this message
        update                      updates helpy if there is a new version
        info                        prints out info about helpy, including constants you've set 
        init project                prepares the current folder for a python project
        init package                prepares the current folder for a python package
        freeze                      pip freeze to create requirements.txt
        serve fastapi               tries to spin up the current project as a fastapi project 
        docker build                builds the image specified in the dockerfile
        docker push                 pushes the image to dockerhub. Set username in .env or from cmd
        package build               uses the setup.py to build the package
        package push                pushes the package to the pypi specified in the .env

    Add the -v flag for verbose output
    Add the -y or -f flag to confirm all dialogs"""
    printout(func="help", msg=helpmessage, doPrint=True)


# endregion

# region UTIL
def pop_arg_or_exit(arglist: [str], errormessage: str):
    """ Tries to pop an arg from the list. If this is not possible: display errormessage and exit """
    if (len(arglist) <= 0):
        printout(func="helpy", msg=f"{errormessage}", doPrint=True)
        sys.exit(1)
    return arglist.pop(0).lower()


def prompt_sure(prompt_text: str) -> None:
    def outer_wrapper(func):
        def wrapper(*args, **kwargs):
            if (input(prompt_text).lower() != 'y'):
                return
            return func(*args, **kwargs)

        return wrapper

    return outer_wrapper


def prompt_yesno(prompt_text: str) -> None:
    if (input(prompt_text).lower() != 'y'):
        print("exiting..")
        exit(0)


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
def load_env_vars(env_file_path: str = None) -> None:
    try:
        from dotenv import load_dotenv
    except ImportError as e:
        subprocess.call(f"{VENVPY} -m pip install python-dotenv --upgrade")
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=env_file_path)


def venv_exists() -> bool:
    return os.path.isfile(VENVPY)


def create_virtualenv(projectfolder: str, verbose: bool = False):
    """ Creates a virtual environment in a project folder """

    if (os.path.exists(os.path.join(projectfolder, 'venv'))):
        printout(func=create_virtualenv.__name__, msg=f"Virtual environment already exists", doPrint=verbose)
        return

    try:
        import venv
    except ImportError as e:
        printout(func=create_virtualenv.__name__, msg=f"Create venv: venv not installed: installing..", doPrint=verbose)
        subprocess.call(f"{VENVPY} -m pip install venv --upgrade")
        printout(func=create_virtualenv.__name__, msg=f"Create venv: venv successfully installed.", doPrint=verbose)
    printout(func=create_virtualenv.__name__, msg=f"Installing virtualenv", doPrint=verbose)
    subprocess.call(f'python.exe -m venv {projectfolder}/venv')
    printout(func=create_virtualenv.__name__, msg=f"Successfully created virtualenv", doPrint=verbose)


# endregion

# region INIT
def init_project(verbose: bool = False, force: bool = False):
    """ Needs certain files and folder structure always. """

    PROJFOLDER = os.getcwd()
    printout(func=init_project.__name__, msg=f"Initializing new project at {PROJFOLDER}..", doPrint=verbose)
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
    download_file(url=f"{FILES_URL}/default_gitignore", filepath=os.path.join(PROJFOLDER, '.gitignore'), verbose=verbose, overwrite=force)
    download_file(url=f"{FILES_URL}/default_readme.md", filepath=os.path.join(PROJFOLDER, 'readme.md'), verbose=verbose, overwrite=force)
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
    download_file(url=f"{FILES_URL}/default_readme.md", filepath=os.path.join(PROJFOLDER, 'readme.md'), verbose=verbose, overwrite=force)
    download_file(url=f"{FILES_URL}/default_setup.cfg", filepath=os.path.join(PROJFOLDER, 'setup.cfg'), verbose=verbose, overwrite=force)
    download_file(url=f"{FILES_URL}/default_setup.py", filepath=os.path.join(PROJFOLDER, 'setup.py'), verbose=verbose, overwrite=force)

    # Adjust files by replacing the project name
    replace_in_file(filepath=os.path.join(PROJFOLDER, 'setup.py'), replace_this_text='{PROJECT_NAME}', replacment_text=package_name)
    replace_in_file(filepath=os.path.join(PROJFOLDER, 'readme.md'), replace_this_text='{PROJECT_NAME}', replacment_text=package_name)

    printout(func=init_project.__name__, msg=f"Project initialized", doPrint=True)


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
        printout(func=pip_freeze.__name__, msg=f"{pip_freeze.__name__} failed: {e}", doPrint=True)


# endregion

# region FASTAPI
def serve_fastapi():
    try:
        subprocess.call('venv/scripts/python.exe -m uvicorn main:app --env-file config/conf/.env --reload')
    except Exception as e:
        printout(func=serve_fastapi.__name__, msg=f"Failed to serve: {e}", doPrint=True)


# endregion

# region docker
def docker_system_prune():
    try:
        subprocess.call(f"docker system prune -f")
    except Exception as e:
        printout(func=docker_system_prune.__name__, msg=f"Docker system prune failed: '{e}'", doPrint=True)


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
        printout(func=docker_build.__name__, msg=f"Failed to build docker image: '{e}", doPrint=True)


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
        printout(func=docker_push.__name__, msg=f"Failed to push docker image: '{e}'", doPrint=True)


# endregion

# region PYPI
def package_build(verbose: bool = False):
    try:
        subprocess.call("rm ./dist/*")
    except Exception as e:
        pass
    pip_freeze(verbose=verbose)
    try:
        import twine
    except ImportError as e:
        subprocess.call("venv/scripts/python.exe -m pip install twine --upgrade")
    subprocess.call(f"{VENVPY} setup.py sdist")


def package_push(verbose: bool = False, force: bool = False, pypi_url: str = None, pypi_username: str = None, pypi_password: str = None):
    """ Pushes the package to pypi server """

    if (not force):
        if (input("Are you sure you want to push the package to PyPi? (y/n)").lower() != 'y'):
            return

    # 1. Ensure username, password and url
    if (pypi_username == None or len(pypi_username) <= 3):      pypi_username = input("PyPi username")
    if (pypi_password == None or len(pypi_password) <= 3):      pypi_password = input("PyPi password")
    if (pypi_url == None or len(pypi_url) <= 3):                pypi_url = input("PyPi url")

    # 2. Ensure twine is installed
    try:
        import twine
    except ImportError as e:
        printout(func=package_push.__name__, msg="twine not installed; installing..", doPrint=verbose)
        subprocess.call("venv/scripts/python.exe -m pip install twine --upgrade")
        printout(func=package_push.__name__, msg="Successfully installed twine", doPrint=verbose)

    # 3. Call package push
    printout(func=package_push.__name__, msg=f"Pushing package to '{pypi_url}'", doPrint=verbose)
    subprocess.call(f'{VENVPY} -m twine upload dist/* --repository-url "{pypi_url}" -u "{pypi_username}" -p "{pypi_password}"')
    printout(func=package_push.__name__, msg=f"Successfully pushed package to '{pypi_url}'", doPrint=True)


# endregion


def main(args: [str]):
    if (len(args) == 0):
        help()
        quit()
    cmd1 = pop_arg_or_exit(arglist=args, errormessage="Helpy expects at least one argument. Check out [helpy help] for more information")

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
        update(force=True, verbose=VERBOSE)
    elif (cmd1 == 'help'):
        help()
    elif (cmd1 == 'info'):
        display_info()
    elif (cmd1 == 'init'):
        # Get init_type
        init_type = pop_arg_or_exit(arglist=args, errormessage="[helpy init] requires another argument. Check out [helpy help] for more information")

        # Functions
        if (init_type == 'project'):
            init_project(force=DO_FORCE, verbose=VERBOSE)
        elif (init_type == 'package'):
            package_name = pop_arg_or_exit(arglist=args, errormessage="[helpy init package] requires another argument: 'package_name'. Example: "
                                                                      "\n\t[helply init package my_package_name]"
                                                                      "\n\tCheck out [helpy help] for more information")
            init_package(package_name=package_name, verbose=VERBOSE, force=DO_FORCE)
        else:
            printout(func="helpy", msg=f"Unknown option for helpy init: '{init_type}'. Check out [helpy help] for more information")
    elif (cmd1 == 'freeze'):
        # pip freeze
        pip_freeze(verbose=VERBOSE)
    elif (cmd1 == 'serve'):
        # Get application type
        app_type = pop_arg_or_exit(arglist=args, errormessage="[helpy serve] requires another argument. Check out [helpy help] for more information")

        if (app_type == 'fastapi'):
            serve_fastapi()
        else:
            printout(func="helpy", msg=f"Unknown option for [helpy serve]: '{app_type}'. Check out [helpy help] for more information")
    elif (cmd1 == 'docker'):
        docker_op = pop_arg_or_exit(arglist=args, errormessage="[helpy docker] requires another argument. Check out [helpy help] for more information")

        if (docker_op == 'build'):
            docker_build(verbose=VERBOSE)
        elif (docker_op == 'push'):
            docker_push(force=DO_FORCE, verbose=VERBOSE)
        else:
            printout(func="helpy", msg=f"Unknown option for [helpy docker]: '{docker_op}'. Check out [helpy help] for more information")
    elif (cmd1 == 'package'):
        package_op = pop_arg_or_exit(arglist=args, errormessage="[helpy package] requires another argument. Check out [helpy help] for more information")

        if (package_op == 'build'):
            package_build(verbose=VERBOSE)
        elif (package_op == 'push'):
            # 1. Check if username and password are set
            username = None
            password = None
            if ((PYPI_URL != None) and (len(PYPI_URL) > 3)):                pypi_url = PYPI_URL
            if ((PYPI_USERNAME != None) and (len(PYPI_USERNAME) > 3)):      username = PYPI_USERNAME
            if ((PYPI_PASSWORD != None) and (len(PYPI_PASSWORD) > 3)):      password = PYPI_PASSWORD

            package_push(verbose=VERBOSE, force=DO_FORCE, pypi_url=pypi_url, pypi_username=username, pypi_password=password)
    else:
        print(f"unknown command: '{args[0]}'")
        help()


# 2022-03-08 16:07
if __name__ == "__main__":
    # PYPI
    # load_env_vars(env_file_path='config/conf/.env')
    PYPI_URL: str = None
    PYPI_USERNAME: str = None  # os.environ.get("PYPI_USER")
    PYPI_PASSWORD: str = None  # os.environ.get("PYPI_PASS")
    # DOCKER
    DOCKER_IMAGE_NAME: str = "docker-hub.datanext.nl/test/test"

    main(sys.argv[1:])


