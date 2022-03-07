import os
import sys
import subprocess
import urllib.request

VENVPY = "venv/scripts/python.exe"


def update(verbose: bool = False, force: bool = False):
    """ Downloads new helpy """

    printout(msg='updating helpy..', doPrint=verbose)

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
                printout(msg="Helpy is up to date", doPrint=True)
            return
        else:
            if (input("Update available! Update? (y/n)").lower() != 'y'):
                printout(msg="Skipping helpy update..", doPrint=True)
                return

    # 3. Combine and write
    newHelpy = gist_content + "\n\n" + curfile_initmain
    with open(__file__, 'w') as file:
        file.write(newHelpy)

    # Feedback
    gist_idx_dateline = gist_idx_initmainline - 1
    printout(msg=f"updated helpy to {gist_lines[gist_idx_dateline].replace('# ', '')}", doPrint=True)


# region UTIL
def helpy_cur_version():
    NAME_MAIN_STRING = 'if __name__ == "__main__":'
    with open(__file__, 'r') as rfile:
        curfile_lines = rfile.read().split("\n")
    curfile_idx_namemainline = curfile_lines.index(NAME_MAIN_STRING)
    curfile_idx_dateline = curfile_idx_namemainline - 1
    curfile_date = curfile_lines[curfile_idx_dateline]
    curfile_date = curfile_date.replace("# ", "")
    return curfile_date
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
def printout(msg: str, doPrint: bool = True):
    if (doPrint):
        print(f"[Helpy] {msg}")
def display_info():
    helpy_version = helpy_cur_version()
    printout(msg=f"""
    HELPY version {helpy_version}
        PYPI:
        PYPI URL: \t {PYPI_URL if (PYPI_URL) else ""}
        PYPI username: \t {PYPI_USERNAME if (PYPI_USERNAME) else ""}
        PYPI password: \t {"*" * len(PYPI_PASSWORD) if (PYPI_PASSWORD) else ""}

        DOCKER:
        image name: \t {DOCKER_IMAGE_NAME if (DOCKER_IMAGE_NAME) else ""}
    """, doPrint=True)
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
# endregion

# region GENERAL
def pip_freeze(verbose: bool = False):
    printout(msg=f"Pip freezing requirements..", doPrint=verbose)
    try:
        python_location = os.path.join(os.getcwd(), VENVPY)
        with open('requirements.txt', 'w') as file_:
            subprocess.call([python_location, '-m', 'pip', 'freeze'], stdout=file_)
        printout(msg=f"Pip freeze requirements succes", doPrint=verbose)
    except Exception as e:
        printout(msg=f"{pip_freeze.__name__} failed: {e}", doPrint=True)
# endregion

# region serve
def serve_fastapi():
    try:
        subprocess.call('venv/scripts/python.exe -m uvicorn main:app --env-file config/conf/.env --reload')
    except Exception as e:
        printout(msg=f"Failed to serve: {e}", doPrint=True)


# endregion

# region docker
def docker_system_prune():
    try:
        subprocess.call(f"docker system prune -f")
    except Exception as e:
        printout(msg=f"Docker system prune failed: '{e}'", doPrint=True)


def docker_build(verbose: bool = False):
    if (len(DOCKER_IMAGE_NAME) < 3):
        printout(msg="Please provide a docker image name in helpy.py", doPrint=True)
        return
    printout(msg=f"Building docker image '{DOCKER_IMAGE_NAME}'..", doPrint=verbose)
    pip_freeze(verbose=verbose)
    try:
        subprocess.call(f'docker build . -t "{DOCKER_IMAGE_NAME}" --secret id=dnxpypi_creds,src=config\conf\.env')
        docker_system_prune()
        printout(msg=f"Successfully built docker image", doPrint=verbose)
    except Exception as e:
        printout(msg=f"Failed to build docker image: '{e}", doPrint=True)


def docker_push(verbose: bool = False, force: bool = False):
    """ Pushes the docker image to the docker hub """

    if (len(DOCKER_IMAGE_NAME) <= 3):
        printout(msg=f"Invalid DOCKER_IMAGE_NAME: '{DOCKER_IMAGE_NAME}'. Please provide a docker image name in helpy.py", doPrint=True)
        return

    if (not force):
        if (input(f"Are you sure you want to push '{DOCKER_IMAGE_NAME}' to dockerhub? (y/n)").lower() != "y"):
            return

    printout(msg=f"Pushing image '{DOCKER_IMAGE_NAME}' to docker hub", doPrint=verbose)
    try:
        subprocess.call(f'docker push "{DOCKER_IMAGE_NAME}"')
        printout(msg=f"Successfully pushed image '{DOCKER_IMAGE_NAME}' to docker hub", doPrint=verbose)
    except Exception as e:
        printout(msg=f"Failed to push docker image: '{e}'", doPrint=True)


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


def package_push(verbose: bool = False, force: bool = False, pypi_username: str = None, pypi_password: str = None):
    """ Pushes the package to pypi server """

    if (not force):
        if (input("Are you sure you want to push the package to PyPi? (y/n)").lower() != 'y'):
            return

    # 1. Ensure username
    if (pypi_username == None):
        pypi_username = input("PyPi username")

    # 2. Ensure password
    if (pypi_password == None):
        pypi_password = input("PyPi password")

    # 3. Ensure pypi url is valid
    if (len(PYPI_URL) <= 3):
        printout(msg=f"PYPI_URL is invalid: '{PYPI_URL}'", doPrint=True)
        return

    # 4. Ensure twine is installed
    try:
        import twine
    except ImportError as e:
        printout(msg="twine not installed; installing..", doPrint=verbose)
        subprocess.call("venv/scripts/python.exe -m pip install twine --upgrade")
        printout(msg="Successfully installed twine", doPrint=verbose)

    # 4. Call package push
    printout(msg=f"Pushing package to '{PYPI_URL}'", doPrint=verbose)
    subprocess.call(f'{VENVPY} -m twine upload dist/* --repository-url "{PYPI_URL}" -u "{pypi_username}" -p "{pypi_password}"')
    printout(msg=f"Successfully pushed package to '{PYPI_URL}'", doPrint=True)


# endregion


def main(args: [str]):
    cmd1 = args[0].lower()
    DO_FORCE = len({'f', 'y'} & set(["".join(a.split("-")) for a in args])) > 0
    VERBOSE = len({'v', 'y'} & set(["".join(a.split("-")) for a in args])) > 0

    # if (cmd1 != "update" and not is_up_to_date()):
    #     res = input("update available! Download? (y/n)")
    #     if (DO_FORCE or res == 'y'):
    #         update()
    if (cmd1 != 'update'):
        # Checks for updates
        update(force=False, verbose=VERBOSE)

    if (cmd1 == 'update'):
        update(force=True, verbose=VERBOSE)
    if (cmd1 == 'info'):
        display_info()
    elif (cmd1 == 'freeze'):
        pip_freeze(verbose=VERBOSE)
    elif (cmd1 == 'serve'):
        serve_fastapi()
    elif (cmd1 == 'docker'):
        if (args[1].lower() == 'build'):
            docker_build(verbose=VERBOSE)
        elif (args[1].lower() == 'push'):
            docker_push(force=DO_FORCE, verbose=VERBOSE)
    elif (cmd1 == 'package'):
        if (args[1].lower() == 'build'):
            package_build(verbose=VERBOSE)
        elif (args[1].lower() == 'push'):
            # 1. Get username and password from args
            cleanargs = [a for a in args[2:] if (a[0] != '-')]
            my_username = PYPI_USERNAME or (cleanargs[0] if (len(cleanargs) >= 1) else None)
            my_password = PYPI_PASSWORD or (cleanargs[1] if (len(cleanargs) >= 2) else None)
            package_push(verbose=VERBOSE, force=DO_FORCE, pypi_username=my_username, pypi_password=my_password)
    else:
        print(f"unknown command: '{args[0]}'")


# 2022-03-07 10:53
if __name__ == "__main__":
    # PYPI
    PYPI_URL: str = "https://pypi.dev.datanext.nl/pypi"
    # load_env_vars(env_file_path='config/conf/.env')
    PYPI_USERNAME: str = None  # os.environ.get("PYPI_USER")
    PYPI_PASSWORD: str = None  # os.environ.get("PYPI_PASS")
    # DOCKER
    DOCKER_IMAGE_NAME: str = None

    main(sys.argv[1:])


