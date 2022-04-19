import webbrowser
from dataclasses import dataclass
import os
import shutil
import sys
import subprocess
import urllib.request



@dataclass
class HelpySettings:
    # project_dir:str = os.getcwd()
    venv_location:str = None
    env_file_path:str = None
    pypi_url:str = None
    pypi_username:str = None
    pypi_password:str = None
    docker_image_name:str = None

    @property
    def python_location(self):
        py_loc = os.path.join(os.getcwd(), f'{self.venv_location}', 'Scripts', 'python.exe') if (self.venv_location) else None
        return py_loc


    def validate(self):

        if (self.pypi_url != None):
            if (len(self.pypi_url) < 5):
                printout(func=".helyp", msg=f"PyPiUrl '{self.pypi_url}' invalid: please provide valid pypi url", doPrint=True)
                quit()
            if ('://' in self.pypi_url or 'http' in self.pypi_url or 'www' in self.pypi_url):
                printout(func=".helyp", msg="PyPi Url invalid: please provide pypi url without 'www.', 'http://' or 'https://' in .helpy", doPrint=True)
                quit()
        if (self.pypi_username != None):
            if (len(self.pypi_username) < 3):
                printout(func=".helyp", msg=f"PyPi Username '{self.pypi_username}' invalid: please provide valid pypi username", doPrint=True)
                quit()
        if (self.pypi_password != None):
            if (len(self.pypi_password) < 3):
                printout(func=".helyp", msg=f"PyPi Password '{self.pypi_password}' invalid: please provide valid pypi password", doPrint=True)
                quit()
        if (self.venv_location == None):
            printout(func=".helyp", msg="VENV_LOCATION invalid: please provide your virtual environment folder location in .helpy", doPrint=True)
            quit()


class Helpy:

    helpy_settings:HelpySettings = None
    project_dir: str = os.getcwd()
    FILES_URL = f"https://raw.githubusercontent.com/mike-huls/helpy/main/files"
    verbose: bool
    force: bool

    def __init__(self, verbose: bool = False, force: bool = False):
        self.project_dir = os.getcwd()
        self.verbose = verbose
        self.force = force
        self.__ensure_helpy_init()

    def __ensure_helpy_init(self) -> None:
        """ Checks whether helpy is init; if not: prompts for consent. No consent = exit """

        helpy_is_init = '.helpy' in os.listdir(self.project_dir)
        if (not helpy_is_init):
            if (input(f"Helpy is not initialized. Initialize helpy at {self.project_dir}? (y/n)").lower() != 'y'):
                printout(func=self.__ensure_helpy_init.__name__, msg="Exiting..", doPrint=True)
                quit()
            self.init_helpy()


    # Initialization
    def init_helpy(self):
        """ Initializes """

        printout(func=self.init_helpy.__name__, msg=f"Initializing helpy at {self.project_dir}..", doPrint=self.verbose)
        FILES_URL = f"https://raw.githubusercontent.com/mike-huls/helpy/main/files"

        # config/conf/.env
        create_folder(folderpath=os.path.join(self.project_dir, 'config'), verbose=self.verbose)
        create_folder(folderpath=os.path.join(self.project_dir, 'config', 'conf'), verbose=self.verbose)
        download_file(url=f"{FILES_URL}/default_env", filepath=os.path.join(self.project_dir, 'config', 'conf', '.env'), verbose=self.verbose, overwrite=self.force)
        download_file(url=f"{FILES_URL}/default_definitions.py", filepath=os.path.join(self.project_dir, 'config', 'definitions.py'), verbose=self.verbose, overwrite=self.force)

        # Create .helpy settings file
        download_file(url=f"{FILES_URL}/default_.helpy", filepath=os.path.join(self.project_dir, '.helpy'), verbose=self.verbose, overwrite=self.force)
        printout(func=self.init_helpy.__name__, msg=f"Initialized helpy. Don't forget to activate the new venv", doPrint=self.verbose)
    def init_project(self, project_name: str = "My Project"):
        """ Needs certain files and folder structure always. """

        printout(func=self.init_project.__name__, msg=f"Initializing new project '{project_name}' at {self.project_dir}..", doPrint=self.verbose)

        # config/conf/.env
        create_folder(folderpath=os.path.join(self.project_dir, 'config'), verbose=self.verbose)
        create_folder(folderpath=os.path.join(self.project_dir, 'config', 'conf'), verbose=self.verbose)
        download_file(url=f"{self.FILES_URL}/default_env", filepath=os.path.join(self.project_dir, 'config', 'conf', '.env'), verbose=self.verbose, overwrite=self.force)
        download_file(url=f"{self.FILES_URL}/default_definitions.py", filepath=os.path.join(self.project_dir, 'config', 'definitions.py'), verbose=self.verbose, overwrite=self.force)

        # Create venv
        # printout(func=self.init_project.__name__, msg=f"Initializing venv..", doPrint=self.verbose)
        # # create_virtualenv(projectfolder=PROJFOLDER, verbose=self.verbose)
        # printout(func=self.init_project.__name__, msg=f"Initialized venv", doPrint=self.verbose)

        # Create default folders
        create_folder(folderpath=os.path.join(self.project_dir, 'doc'), verbose=self.verbose)
        create_folder(folderpath=os.path.join(self.project_dir, 'services'), verbose=self.verbose)
        download_file(url=f"{self.FILES_URL}/default_doc.md", filepath=os.path.join(self.project_dir, 'doc', 'example.md'), verbose=self.verbose, overwrite=self.force)
        create_folder(folderpath=os.path.join(self.project_dir, 'test'), verbose=self.verbose)
        create_empty_file(filepath=os.path.join(self.project_dir, 'test', '__init__.py'), verbose=self.verbose)
        download_file(url=f"{self.FILES_URL}/default_test.py", filepath=os.path.join(self.project_dir, 'test', 'test_functions.py'), verbose=self.verbose, overwrite=self.force)

        # Create default files (with content)
        download_file(url=f"{self.FILES_URL}/default_gitignore", filepath=os.path.join(self.project_dir, '.gitignore'), verbose=self.verbose, overwrite=self.force)
        download_file(url=f"{self.FILES_URL}/default_readme_project.md", filepath=os.path.join(self.project_dir, 'README.md'), verbose=self.verbose, overwrite=self.force)
        replace_in_file(filepath=os.path.join(self.project_dir, 'README.md'), replace_this_text='{PROJECT_NAME}', replacment_text=project_name)
        download_file(url=f"{self.FILES_URL}/default_main.py", filepath=os.path.join(self.project_dir, 'main.py'), verbose=self.verbose, overwrite=self.force)
        download_file(url=f"{self.FILES_URL}/default_Dockerfile", filepath=os.path.join(self.project_dir, 'Dockerfile'), verbose=self.verbose, overwrite=self.force)
        download_file(url=f"{self.FILES_URL}/default_dockerignore", filepath=os.path.join(self.project_dir, '.dockerignore'), verbose=self.verbose, overwrite=self.force)

        printout(func=self.init_project.__name__, msg=f"Project initialized", doPrint=True)
    def init_package(self, package_name: str):
        """ Get files and folder structure"""
        printout(func=self.init_package.__name__, msg=f"Initializing new project at {self.project_dir}..", doPrint=self.verbose)

        # Create default folders
        create_folder(folderpath=os.path.join(self.project_dir, 'doc'), verbose=self.verbose)
        create_folder(folderpath=os.path.join(self.project_dir, 'services'), verbose=self.verbose)
        download_file(url=f"{self.FILES_URL}/default_doc.md", filepath=os.path.join(self.project_dir, 'doc', 'example.md'), verbose=self.verbose, overwrite=self.force)
        create_folder(folderpath=os.path.join(self.project_dir, 'test'), verbose=self.verbose)
        create_empty_file(filepath=os.path.join(self.project_dir, 'test', '__init__.py'), verbose=self.verbose)
        download_file(url=f"{self.FILES_URL}/default_test.py", filepath=os.path.join(self.project_dir, 'test', 'test_functions.py'), verbose=self.verbose, overwrite=self.force)

        # Create default files (with content)
        download_file(url=f"{self.FILES_URL}/default_gitignore", filepath=os.path.join(self.project_dir, '.gitignore'), verbose=self.verbose, overwrite=self.force)
        download_file(url=f"{self.FILES_URL}/default_readme_package.md", filepath=os.path.join(self.project_dir, 'README.md'), verbose=self.verbose, overwrite=self.force)
        replace_in_file(filepath=os.path.join(self.project_dir, 'README.md'), replace_this_text='{PROJECT_NAME}', replacment_text=package_name)
        download_file(url=f"{self.FILES_URL}/default_setup.cfg", filepath=os.path.join(self.project_dir, 'setup.cfg'), verbose=self.verbose, overwrite=self.force)
        download_file(url=f"{self.FILES_URL}/default_setup.py", filepath=os.path.join(self.project_dir, 'setup.py'), verbose=self.verbose, overwrite=self.force)
        replace_in_file(filepath=os.path.join(self.project_dir, 'setup.py'), replace_this_text='{PROJECT_NAME}', replacment_text=package_name)

        # Create module folder with __init__.py
        create_folder(folderpath=os.path.join(self.project_dir, package_name), verbose=self.verbose)
        create_empty_file(filepath=os.path.join(self.project_dir, package_name, '__init__.py'), verbose=self.verbose)

        printout(func=self.init_package.__name__, msg=f"Project initialized", doPrint=True)
    def init_fastapi(self, api_name: str):
        """ Get files and folder structure"""
        printout(func=self.init_project.__name__, msg=f"Initializing new project '{api_name}' at {self.project_dir}..", doPrint=self.verbose)

        # config/conf/.env
        create_folder(folderpath=os.path.join(self.project_dir, 'config'), verbose=self.verbose)
        create_folder(folderpath=os.path.join(self.project_dir, 'config', 'conf'), verbose=self.verbose)
        download_file(url=f"{self.FILES_URL}/default_env", filepath=os.path.join(self.project_dir, 'config', 'conf', '.env'), verbose=self.verbose, overwrite=self.force)
        download_file(url=f"{self.FILES_URL}/default_definitions.py", filepath=os.path.join(self.project_dir, 'config', 'definitions.py'), verbose=self.verbose, overwrite=self.force)

        # Create default folders
        create_folder(folderpath=os.path.join(self.project_dir, 'services'), verbose=self.verbose)
        # doc
        create_folder(folderpath=os.path.join(self.project_dir, 'doc'), verbose=self.verbose)
        download_file(url=f"{self.FILES_URL}/default_doc.md", filepath=os.path.join(self.project_dir, 'doc', 'example.md'), verbose=self.verbose, overwrite=self.force)
        # routes/meta/default_healthRoute.py
        create_folder(folderpath=os.path.join(self.project_dir, 'routes'), verbose=self.verbose)
        create_folder(folderpath=os.path.join(self.project_dir, 'routes', 'meta'), verbose=self.verbose)
        download_file(url=f"{self.FILES_URL}/default_healthRoute.py", filepath=os.path.join(self.project_dir, 'routes', 'meta', 'healthRoute.py'), verbose=self.verbose, overwrite=self.force)
        download_file(url=f"{self.FILES_URL}/default_healthRouteModels.py", filepath=os.path.join(self.project_dir, 'routes', 'meta', 'healthRouteModels.py'), verbose=self.verbose, overwrite=self.force)

        # test
        create_folder(folderpath=os.path.join(self.project_dir, 'test'), verbose=self.verbose)
        create_empty_file(filepath=os.path.join(self.project_dir, 'test', '__init__.py'), verbose=self.verbose)
        download_file(url=f"{self.FILES_URL}/default_test.py", filepath=os.path.join(self.project_dir, 'test', 'test_functions.py'), verbose=self.verbose, overwrite=self.force)

        # Create default files (with content)
        download_file(url=f"{self.FILES_URL}/default_gitignore", filepath=os.path.join(self.project_dir, '.gitignore'), verbose=self.verbose, overwrite=self.force)
        download_file(url=f"{self.FILES_URL}/default_readme_project.md", filepath=os.path.join(self.project_dir, 'README.md'), verbose=self.verbose, overwrite=self.force)
        replace_in_file(filepath=os.path.join(self.project_dir, 'README.md'), replace_this_text='{API_NAME}', replacment_text=api_name)
        download_file(url=f"{self.FILES_URL}/default_main_fastapi.py", filepath=os.path.join(self.project_dir, 'main.py'), verbose=self.verbose, overwrite=self.force)
        replace_in_file(filepath=os.path.join(self.project_dir, 'main.py'), replace_this_text='{API_NAME}', replacment_text=api_name)
        download_file(url=f"{self.FILES_URL}/default_Dockerfile", filepath=os.path.join(self.project_dir, 'Dockerfile'), verbose=self.verbose, overwrite=self.force)
        download_file(url=f"{self.FILES_URL}/default_dockerignore", filepath=os.path.join(self.project_dir, '.dockerignore'), verbose=self.verbose, overwrite=self.force)

        printout(func=self.init_project.__name__, msg=f"Project initialized", doPrint=True)

    # Loading .helpy and .env
    def load_helpy_settings(self, force:bool=False) -> None:
        if (self.helpy_settings != None and not force):
            return

        # 1. Load .helpy as a dict
        _helpySettings:dict = self.__read_helpy_settings()

        # 2. Does helpySettings contain a value that refers to an .env file?
        refers_to_env_file:bool = any([v[:2] == "${" for v in list(_helpySettings.values()) if (v != None)])
        if (refers_to_env_file):
            _helpySettings = self.__load_env_vars_in_helpysettings(_helpySettings)

        helpy_settings = HelpySettings(**_helpySettings)
        helpy_settings.validate()
        self.helpy_settings = helpy_settings
    def __read_helpy_settings(self) -> dict:
        """ Reads the content of .helpy into a HelpySettings and returns """

        # 1. Read the .helpy file
        helpysettings_path = os.path.join(self.project_dir, '.helpy')

        # 2. Read .helpy into a dict after cleaning. Then load the dict into a HelpySettings instance
        helpySettingsDict = {}
        with open(helpysettings_path) as file:
            helpySettings_lines = [l.replace("\n", "") for l in file.readlines() if (l[0] != "#" and "=" in l)]
            for line in helpySettings_lines:

                # Reading and cleanup
                k, v = line.split("=")
                k = k.lower()

                # If v is not set it is ''. Convert to None
                v = None if (v == '') else v

                # Remove start and end quotes if values is set
                if (v != None):
                    for ch in ["'", '"']:
                        if (v[0] == ch and v[-1] == ch):
                            v = v[1:-1]

                helpySettingsDict[k] = v

        return helpySettingsDict
    def __load_env_vars_in_helpysettings(self, helpySettingsDict:dict) -> dict:
        """ Replaces ${these_values} in .helpy with variables from the specified .env file """

        # 1. Check if we have a path to the env file
        env_file_path_key = "env_file_path"
        if (env_file_path_key not in list(helpySettingsDict)):
            printout(func="read_helpy_env_vars", msg=f"Missing key in .helpy file: {env_file_path_key.upper()}. Exiting..", doPrint=True)
            quit()
        if (helpySettingsDict.get(env_file_path_key) == None):
            printout(func="read_helpy_env_vars", msg=f"Missing value in .helpy file for key {env_file_path_key.upper()}. Exiting..", doPrint=True)
            quit()

        # 2. Get the full path to the .env file and check if there is a file there
        envfullpath = os.path.join(self.project_dir, helpySettingsDict.get(env_file_path_key))
        if (not os.path.isfile(envfullpath)):
            printout(
                func=f"{self.__read_helpy_settings.__name__}",
                msg=f"The .env file you specified in .helpy does not exist\n"
                    f"Please create a .env file at {envfullpath}\n"
                    f"Exiting..", doPrint=True)
            quit()
            # if (helpySettings.env_file_path)

        # 3. Load the env file into a dict
        env_vars:dict = self.__read_env_file(env_file_path=envfullpath)

        # 4. Replace ${variables} in helpySettings with values from env var is specified
        for k, v in helpySettingsDict.items():
            if (v == '' or v == None):
                continue
            if (v[:2] == '${'):
                envfileVal = env_vars.get(v[2:-1])  # gets rid of ${ ... }
                if (envfileVal == None):
                    printout(
                        func=f"{self.__read_helpy_settings.__name__}",
                        msg=f"You specified a key in .helpy that cannot be found in your .env.\n"
                            f"Please check if key '{v[2:-1]}' exists in the .env at {envfullpath})\n"
                            f"Exiting..",
                        doPrint=True
                    )
                    quit()
                helpySettingsDict[k] = envfileVal

        # 6. Helpy settings
        return helpySettingsDict
    def __read_env_file(self, env_file_path: str) -> dict:
        """ Loads the values from the specified env_file into the environment """

        returnDict = {}
        with open(env_file_path, 'r') as file:
            envfile_lines = [l.replace("\n", "") for l in file.readlines() if l[0] != "#"]
            for line in envfile_lines:
                kv: [str] = line.split("=")
                k: str
                v: str
                if (len(kv) <= 1):
                    continue
                else:
                    k = kv[0]
                    v = kv[1] if (len(kv) == 2) else "=".join(kv[1:])
                if (len(v) <= 0):
                    continue
                v = v.strip("'")
                v = v.strip('"')
                returnDict[k] = v
        return returnDict
    def __prep_env_file(self):

        # Read in the file
        with open(self.helpy_settings.env_file_path, 'r') as file:
            filedata = file.read()
        # Write the file out again
        with open(self.helpy_settings.env_file_path, 'w', newline="\n") as file:
            file.write(filedata)

    # Print info about helpy
    def update(self) -> None:
        """ Downloads new helpy """

        printout(func=self.update.__name__, msg='updating helpy..', doPrint=self.verbose)

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
        if (not self.force):
            helpy_up_to_date = curfile_date == remote_date
            if (helpy_up_to_date):
                printout(func=self.update.__name__, msg="Helpy is up to date", doPrint=self.verbose)
                return
            else:
                printout(func='helpy', msg="Update available! Update? (y/n)", doPrint=True)
                if (input("").lower() != 'y'):
                    printout(func=self.update.__name__, msg="Skipping helpy update..", doPrint=True)
                    return

        # 3. Combine and write
        newHelpy = remote_content + "\n" + curfile_initmain
        with open(__file__, 'w') as file:
            file.write(newHelpy)

        # Feedback
        remote_idx_dateline = remote_idx_initmainline - 1
        printout(func=self.update.__name__, msg=f"updated helpy to {remote_lines[remote_idx_dateline].replace('# ', '')}", doPrint=True)
    def helpy_cur_version(self) -> str:
        NAME_MAIN_STRING = 'if __name__ == "__main__":'
        with open(__file__, 'r') as rfile:
            curfile_lines = rfile.read().split("\n")
        curfile_idx_namemainline = curfile_lines.index(NAME_MAIN_STRING)
        curfile_idx_dateline = curfile_idx_namemainline - 1
        curfile_date = curfile_lines[curfile_idx_dateline]
        curfile_date = curfile_date.replace("# ", "")
        return curfile_date
    def display_info(self) -> None:
        """ """


        self.load_helpy_settings()

        process = subprocess.Popen([f'{self.helpy_settings.python_location}', '-V'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = process.communicate()
        python_version = out.decode("utf-8").strip("\r").strip("\n")

        print(
        f"""HELPY version {self.helpy_cur_version()}

        ENVIRONMENT
        VENV_LOCATION: \t {self.helpy_settings.venv_location}
        ENV_FILE_PATH: \t {self.helpy_settings.env_file_path}
        VENV Python: \t {python_version}

        PYPI:
        PYPI URL: \t {self.helpy_settings.pypi_url if (self.helpy_settings.pypi_url) else ""}
        PYPI username: \t {self.helpy_settings.pypi_username if (self.helpy_settings.pypi_username) else ""}
        PYPI password: \t {"*" * len(self.helpy_settings.pypi_password) if (self.helpy_settings.pypi_password) else ""}

        DOCKER:
        image name: \t {self.helpy_settings.docker_image_name if (self.helpy_settings.docker_image_name) else ""}
        """)
    def helpy_help(self):
        helpmessage = f"""
        Welcome to Helpy (v.{self.helpy_cur_version()})
        Call [python helpy.py] with any of the following commands:
            help                            display this message
            info                            displays information about helpy, including constants you've set
            version                         displays information about the current version of helpy 
            update                          updates helpy if there is a new version
            create venv                     Creates a virtualenv
            init project                    prepares the current folder for a python project
            init package                    prepares the current folder for a python package
            init fastapi                    prepares the current folder for a FastAPI project
            serve fastapi                   tries to spin up the current project as a fastapi project 
            docker build                    builds the image specified in the dockerfile
            docker run                      runs your image (port_host:port_container, -d for detached (default False), -e to pass .env file (default False)
            docker push                     pushes the image to dockerhub. Set username in .env or from cmd (add --prune to prune afterwards)
            docker prune                    performs a docker system prune to clean up your system
            package build                   uses the setup.py to build the package
            package push                    pushes the package to the pypi specified in the .env
            pip install [packagename]       installs one or more packages (space seperated) using pypi OR the pypi specified in helpy (PYPI_URL)
            pip install requirements.txt    installs a requirements.txt file using pypi OR the pypi specified in the helpy (PYPI_URL)
            pip freeze                      freezes all dependencies in a requirements.txt
            test                            Unittests all test in the /test folder and adds a coverage html. Add --no-coverage to disable generating coverage 
        Add the -v flag for verbose output
        Add the -y or -f flag to confirm all dialogs"""
        printout(func="help", msg=helpmessage, doPrint=True)

    # Installing packages
    def ensure_package_installed(self, package_name: str, import_package_name:str=None):
        """ Makes sure a package is installed """

        if (not self.package_is_installed(package_name=package_name) and not self.package_is_installed(import_package_name)):
            if (input(f"Package '{package_name}' is not installed. \n"
                  f"  (venv location: {self.helpy_settings.python_location})\n"
                  f"  pip install {package_name}? (y/n)".lower()
            ) != 'y'):
                printout(func=f"{self.ensure_package_installed.__name__}.{self.ensure_package_installed.__name__}.", msg=f"Exiting..", doPrint=True)
                quit()
            self.install_package(package_names=[package_name])
    def package_is_installed(self, package_name:str=None) -> bool:
        """ Returns t/f depending on whether a package is installed in this project
            :arg package_name   str     name of the package you're checking
        """

        if (package_name == None or package_name == 'venv'):
            return False

        # Get pip list output and make neat
        process = subprocess.Popen([f'{self.helpy_settings.python_location}', '-m', 'pip', 'list'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = process.communicate()
        list_output = out.decode("utf-8").split("\n")[2:]
        packages = [pline.split(" ")[0] for pline in list_output if (pline != '')]


        return package_name in packages
        # quit()
        # return importlib.util.find_spec(package_name) != None
    def install_package(self, package_names:[str], install_globally:bool=False, upgrade:bool=False) -> None:
        """ Wrapper around pip install """

        printout(func=self.package_build.__name__, msg=f"Installing packages..", doPrint=True)

        # 1. Add extra-index-url?
        extra_index_url = ""
        if (self.helpy_settings.pypi_url != None and self.helpy_settings.pypi_url != None and self.helpy_settings.pypi_url != None):
            extra_index_url = f"--extra-index-url https://{self.helpy_settings.pypi_username}:{self.helpy_settings.pypi_password}@{self.helpy_settings.pypi_url}"

        # 2. Create and execute install command
        do_upgrade = "--upgrade" if upgrade else ""
        cmd_install: str = f"pip install {extra_index_url} {' '.join(package_names)} {do_upgrade}"
        if (not install_globally):
            cmd_install = f"{self.helpy_settings.python_location} -m" + cmd_install
        # cmd_install: str = f"{self.helpy_settings.python_location} -m pip install {extra_index_url} {' '.join(package_names)} --upgrade"
        try:
            if (self.verbose):
                subprocess.call(cmd_install)
            else:
                subprocess.check_output(cmd_install)
            printout(func=self.install_package.__name__, msg=f"Installed {', '.join(package_names)}", doPrint=True)
        except subprocess.CalledProcessError as e:
            printout(func=self.package_build.__name__, msg=f"Error building package: {e}", doPrint=self.verbose)
    def install_requirements_txt(self) -> None:
        """ """

        # 1. Does the requirments.txt file exits in the project dir?
        if (not os.path.isfile(os.path.join(self.project_dir, 'requirements.txt'))):
            printout(func=self.install_package.__name__, msg=f"requirements.txt does not exist", doPrint=True)
            quit()


        # 2. Add extra-index-url?
        extra_index_url = ""
        if (self.helpy_settings.pypi_url != None and self.helpy_settings.pypi_url != None and self.helpy_settings.pypi_url != None):
            extra_index_url = f"--extra-index-url https://{self.helpy_settings.pypi_username}:{self.helpy_settings.pypi_password}@{self.helpy_settings.pypi_url}"

        cmd_install: str = f"{self.helpy_settings.python_location} -m pip install {extra_index_url} -r requirements.txt --upgrade"
        try:
            if (self.verbose):
                subprocess.call(cmd_install)
            else:
                subprocess.check_output(cmd_install)
            printout(func=self.install_package.__name__, msg=f"Installed requirements.txt", doPrint=True)
        except subprocess.CalledProcessError as e:
            printout(func=self.package_build.__name__, msg=f"Error installing requirements.txt: {e}", doPrint=self.verbose)
    def pip_freeze(self):
        printout(func=self.pip_freeze.__name__, msg=f"Pip freezing requirements..", doPrint=self.verbose)
        try:
            with open('requirements.txt', 'w') as file_:
                try:
                    subprocess.call([self.helpy_settings.python_location, '-m', 'pip', 'freeze'], stdout=file_)
                except subprocess.CalledProcessError as e:
                    printout(func=self.pip_freeze.__name__, msg=f"Error executing pip freeze. Exception: {e}", doPrint=self.verbose)
            printout(func=self.pip_freeze.__name__, msg=f"Success", doPrint=True)
        except Exception as e:
            printout(func=self.pip_freeze.__name__, msg=f"Pip freeze failed: \n\t'{e}'", doPrint=True)

    # Building packages
    def package_build(self):
        """ packages code in current directory to the dist folder """

        # 1. Make sure there is an empty dist folder in the project root
        dist_folder_path = os.path.join(os.getcwd(), 'dist')
        if (os.path.isdir(dist_folder_path)):
            printout(func=self.package_build.__name__, msg=f"removing content of dist folder at {dist_folder_path}", doPrint=self.verbose)
            remove_folder(folderpath=dist_folder_path, verbose=False)
            create_folder(folderpath=dist_folder_path, verbose=False)
            printout(func=self.package_build.__name__, msg=f"removed content of dist folder at {dist_folder_path}", doPrint=self.verbose)


        # 2. Call setup function
        setup_cmd = f"{self.helpy_settings.python_location} setup.py sdist"
        try:
            if (self.verbose):
                subprocess.call(setup_cmd)
            else:
                subprocess.check_output(setup_cmd)
        except subprocess.CalledProcessError as e:
            printout(func=self.package_build.__name__, msg=f"Error building package: {e}", doPrint=self.verbose)
    def package_push(self):
        """ Pushes the package to pypi server """

        pypi_url = f"https://{self.helpy_settings.pypi_url}" if (self.helpy_settings.pypi_url) else None
        pypi_username = self.helpy_settings.pypi_username
        pypi_password = self.helpy_settings.pypi_password

        # 2. Make sure we have the correct pypi url
        printout(func=f"{self.package_push.__name__}", msg=f"PyPi Url: {pypi_url}", doPrint=self.verbose)

        # 3. Prompt sure if required
        if (not self.force):
            if (input("Are you sure you want to push the package to PyPi? (y/n)").lower() != 'y'):
                return

        # 4. Push the package
        printout(func=self.package_push.__name__, msg=f"Pushing package to '{pypi_url}'", doPrint=self.verbose)
        try:
            private_pypi_url = f'--repository-url "{pypi_url}"' if (pypi_url != None) else ''
            cmd_push_package = f'{self.helpy_settings.python_location} -m twine upload dist/* {private_pypi_url} -u "{pypi_username}" -p "{pypi_password}"'
            if (self.verbose):
                subprocess.call(cmd_push_package)
            else:
                subprocess.check_output(cmd_push_package)
            printout(func=self.package_push.__name__, msg=f"Successfully pushed package to '{pypi_url}'", doPrint=self.verbose)
        except subprocess.CalledProcessError as e:
            printout(func=self.package_push.__name__, msg=f"Failed push package to '{pypi_url}': \n\t'{e}'", doPrint=True)

    # Virtual environment
    def ensure_venv(self, python_path:str=None):
        """ Creates a virtual environment in a project folder """

        # 1. Venv location is set
        pypath = python_path if (python_path != None) else "python.exe"
        if (self.helpy_settings.venv_location == None):
            printout(func="ensure_venv", msg=f"Provided venv path ('{self.helpy_settings.venv_location}') is not set. Please specify the location of your virtualenv in .helpy.", doPrint=True)
            quit()

        # 2. Check if venv exists
        venv_folder_path_full = os.path.join(self.project_dir, self.helpy_settings.venv_location)
        venv_folder_exists:bool = os.path.isdir(os.path.join(venv_folder_path_full))
        venv_python_exists:bool = os.path.isfile(self.helpy_settings.python_location)

        # 3. Check if venv exists and ask to create venv if it doesnt
        if (venv_folder_exists and venv_python_exists):
            printout(func="ensure_venv", msg=f"Venv exists.", doPrint=self.verbose)
            return
        if (not self.force):
            if (input(f"Virtual env not detected. Create venv at {venv_folder_path_full} with python {pypath}? (y/n)").lower() != 'y'):
                printout(func="ensure_venv", msg=f"Venv not created. Exiting..", doPrint=True)
                quit()

        # 4. Install virtualenv and create venv
        if (not self.package_is_installed(package_name='venv')):
            printout(func="ensure_venv", msg=f"Installing venv", doPrint=self.verbose)
            self.install_package(package_names=['venv'], install_globally=True)
        cmd_create_venv = f'{pypath} -m venv {venv_folder_path_full}'
        printout(func="ensure_venv", msg=f"Creating venv..", doPrint=True)
        subprocess.call(cmd_create_venv)
        printout(func="ensure_venv", msg=f"Venv created", doPrint=True)

    # Serve
    def serve_fastapi(self, port:int=8000):
        """ Makes it so that you can serve fastapi"""

        # 1. Serve fastapi
        printout(func=self.serve_fastapi.__name__, msg=f"Serving FastAPI at localhost:{port}", doPrint=True)

        env_file_add = f"--env-file {self.helpy_settings.env_file_path}" if (self.helpy_settings.env_file_path) else ""
        cmd_serve = f'{self.helpy_settings.python_location} -m uvicorn main:app {env_file_add} --reload --port {port}'
        try:
            webbrowser.open(f"http://localhost:{port}", new=2)
            if (self.verbose):
                subprocess.call(cmd_serve)
            else:
                subprocess.check_output(cmd_serve)

        except subprocess.CalledProcessError as e:
            printout(func=self.serve_fastapi.__name__, msg=f"Error building package: {e}", doPrint=self.verbose)

    # Docker
    def docker_system_prune(self):
        try:
            subprocess.call(f"docker system prune -f")
        except Exception as e:
            printout(func=self.docker_system_prune.__name__, msg=f"Docker system prune failed: \t\n'{e}'", doPrint=True)
    def docker_build(self, prune_afterwards:bool):

        docker_image_name = self.helpy_settings.docker_image_name
        if (docker_image_name == None or len(docker_image_name) < 3):
            printout(func=self.docker_build.__name__, msg="Please provide a docker image name in .helpy", doPrint=True)
            quit()
        printout(func=self.docker_build.__name__, msg=f"Building docker image '{docker_image_name}'..", doPrint=self.verbose)
        try:
            # Remove \r from .env file (if created on windows
            self.__prep_env_file()
            cmd_docker_build = f'docker build -t "{docker_image_name}" --secret id=pypi_creds,src={self.helpy_settings.env_file_path} . '
            if (self.verbose):
                subprocess.call(cmd_docker_build)
            else:
                subprocess.check_output(cmd_docker_build)
            if (prune_afterwards):
                self.docker_system_prune()
            printout(func=self.docker_build.__name__, msg=f"Successfully built docker image", doPrint=self.verbose)
        except subprocess.CalledProcessError as e:
            printout(func=self.docker_build.__name__, msg=f"Failed to build docker image: \n\t'{e}", doPrint=True)
    def docker_run(self, port_host:int=None, port_container:int=None, detached:bool=False, pass_env_file:bool=False):
        """ Runs your contianer """


        docker_image_name = self.helpy_settings.docker_image_name
        if (docker_image_name == None or len(docker_image_name) < 3):
            printout(func=self.docker_build.__name__, msg="Please provide a docker image name in .helpy", doPrint=True)
            quit()
        printout(func=self.docker_build.__name__, msg=f"Running docker container from image '{docker_image_name}'..", doPrint=self.verbose)

        port_mapping = f"-p {port_host}:{port_container}" if (port_host != None and port_container != None) else ""
        pass_env_str = f"--env-file {self.helpy_settings.env_file_path}" if pass_env_file else ""
        try:
            # Remove \r from .env file (if created on windows
            cmd_docker_run = f'docker run {port_mapping} {pass_env_str} {docker_image_name} {"-d" if detached else ""} '
            if (self.verbose):
                subprocess.call(cmd_docker_run)
            else:
                subprocess.check_output(cmd_docker_run)
            printout(func=self.docker_build.__name__, msg=f"Run docker container success", doPrint=self.verbose)
        except subprocess.CalledProcessError as e:
            printout(func=self.docker_build.__name__, msg=f"Failed to build docker image: \n\t'{e}", doPrint=True)
    def docker_push(self):
        """ Pushes the docker image to the docker hub """

        docker_image_name = self.helpy_settings.docker_image_name
        if (len(docker_image_name) <= 3):
            printout(func=self.docker_push.__name__, msg=f"Invalid DOCKER_IMAGE_NAME: '{docker_image_name}'. Please provide a docker image name in helpy.py", doPrint=True)
            return

        if (not self.force):
            if (input(f"Are you sure you want to push '{docker_image_name}' to dockerhub? (y/n)").lower() != "y"):
                return

        printout(func=self.docker_push.__name__, msg=f"Pushing image '{docker_image_name}' to docker hub", doPrint=self.verbose)
        try:
            subprocess.call(f'docker push "{docker_image_name}"')
            printout(func=self.docker_push.__name__, msg=f"Successfully pushed image '{docker_image_name}' to docker hub", doPrint=self.verbose)
        except Exception as e:
            printout(func=self.docker_push.__name__, msg=f"Failed to push docker image: \n\t'{e}'", doPrint=True)

    # Testing + Coverage
    def coveragetest(self, add_html: bool = True):
        """ Creates coveragetest """

        cmd_run_tests = f"""{self.helpy_settings.python_location}  -m unittest discover"""
        cmd_generate_html:str
        if (add_html):
            cmd_run_tests = f"""{self.helpy_settings.python_location} -m coverage run -m unittest discover"""
            cmd_generate_html = f"""{self.helpy_settings.python_location} -m coverage html --omit="*/test*" """

        try:
            if (self.verbose):
                subprocess.call(cmd_run_tests)
            else:
                subprocess.check_output(cmd_run_tests)
            printout(func=self.coveragetest.__name__, msg=f"Ran tests", doPrint=True)
        except subprocess.CalledProcessError as e:
            printout(func=self.coveragetest.__name__, msg=f"Error running tests: {e}", doPrint=self.verbose)


        if (add_html):
            try:
                if (self.verbose):
                    subprocess.call(cmd_generate_html)
                else:
                    subprocess.check_output(cmd_generate_html)
                printout(func=self.coveragetest.__name__, msg=f"Generated coverage html", doPrint=True)
            except subprocess.CalledProcessError as e:
                printout(func=self.coveragetest.__name__, msg=f"Error generating coverage html: {e}", doPrint=self.verbose)

            htmlfilepath = os.path.join(self.project_dir, 'htmlcov', 'index.html')
            webbrowser.open(htmlfilepath, new=2)


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



def main():
    """ Parse command line """
    args = sys.argv[1:]


    # Preferences
    DO_FORCE = '-f' in args
    args.remove('-f') if ('-f' in args) else None
    VERBOSE = '-v' in args
    args.remove('-v') if ('-v' in args) else None


    # Init HELPY
    helpyItself = Helpy(verbose=VERBOSE, force=DO_FORCE)  # Inits helpy and loads the settings (and optionally the .env file) and validate


    # Parse arguments - Must provide at least one argument
    if (len(args) == 0):
        helpyItself.helpy_help()
        quit()
    cmd1 = pop_arg_or_exit(arglist=args, errormessage="Helpy expects at least one argument. Check out [helpy.py help] for more information")


    # Check for updates
    if (cmd1 != 'update'):      helpyItself.update()

    # HELPY functions
    if (cmd1 == 'update'):      helpyItself.update()
    elif (cmd1 == 'help'):      helpyItself.helpy_help()
    elif (cmd1 == 'info'):      helpyItself.display_info()
    elif (cmd1 == 'version'):   print(f"Helpy version {helpyItself.helpy_cur_version()}")
    elif (cmd1 == 'init'):
        # Get init_type
        init_type = pop_arg_or_exit(arglist=args, errormessage="[helpy.py init] requires another argument. Check out [helpy.py help] for more information")

        # Functions
        if (init_type == 'helpy'):
            #
            helpyItself = Helpy(verbose=VERBOSE, force=DO_FORCE)
        elif (init_type == 'project'):
            project_name = args[0] if (len(args) > 0) else None
            if (project_name == None):
                project_name = input("Project name?")
            helpyItself.init_project(project_name=project_name)
        elif (init_type == 'package'):
            package_name = args[0] if (len(args) > 0) else None
            if (package_name == None):
                package_name = input("What is this package called?")
                helpyItself.init_package(package_name=package_name)
        elif (init_type == 'fastapi'):
            api_name = args[0] if (len(args) > 0) else None
            if (api_name == None):
                api_name = input("What is this API called?")
            helpyItself.init_fastapi(api_name=api_name)
        else:
            printout(func="helpy", msg=f"Unknown option for helpy init: '{init_type}'. Check out [helpy.py help] for more information")
    elif (cmd1 == 'create'):
        create_op = pop_arg_or_exit(arglist=args, errormessage="[helpy.py create] requires another argument. Check out [helpy.py help] for more information")

        # Functions
        if (create_op in ['venv', 'virtualenv']):
            helpyItself.load_helpy_settings()

            pypath = input("Please provide the path to your verion of python.exe you would like the venv to be based on (leave empty for default Python:")
            helpyItself.ensure_venv(python_path=pypath)
        else:
            printout(func="helpy", msg=f"Unknown option for helpy create: '{create_op}'. Check out [helpy.py help] for more information")

    # Regular functions (we need helpy settings and venv for this
    else:
        # Make sure we load the settings and have an .env
        helpyItself.load_helpy_settings()
        helpyItself.ensure_venv()

        if (cmd1 == 'serve'):
            # Get application type
            available_apps = ['fastapi']
            serve_op = pop_arg_or_exit(
                arglist=args,
                errormessage="[helpy.py serve] requires another argument. Example: [helpy.py serve <apptype>]. "
                             "Check out a list of available apps at [helpy.py serve list]")


            if (serve_op == 'list'):
                printout(func="helpy", msg=f"Available apps: {available_apps} \t\t Example: [helpy.py serve {available_apps[0]}]")
            elif (serve_op == 'fastapi'):
                targetport = None
                if ('-p' in args):
                    try:
                        targetport = args[args.index('-p') + 1]
                    except Exception as e:
                        printout(func="helpy", msg=f"Invalid argumetn for port -p. Please provide port like '-p 8000' for example")
                        quit()
                helpyItself.ensure_package_installed(package_name='fastapi')
                helpyItself.ensure_package_installed(package_name='uvicorn')
                helpyItself.ensure_package_installed(package_name='python-dotenv', import_package_name='dotenv')
                if (targetport == None):
                    helpyItself.serve_fastapi()
                else:
                    helpyItself.serve_fastapi(port=targetport)
            else:
                printout(func="helpy", msg=f"Unknown option for [helpy.py serve]: '{serve_op}'. Check out [helpy.py serve list] for more information")
        elif (cmd1 == 'docker'):
            docker_op = pop_arg_or_exit(arglist=args, errormessage="[helpy.py docker] requires another argument. Check out [helpy.py help] for more information")
            if (docker_op == 'build'):
                helpyItself.pip_freeze()
                helpyItself.docker_build(prune_afterwards='--prune' in args)
            elif (docker_op == 'run'):

                # Get ports for host and container
                port_arg = [a for a in args if (':' in a)]
                port_host, port_container = port_arg[0].split(":") if (len(port_arg) > 0) else (None, None)


                helpyItself.docker_run(port_host=port_host, port_container=port_container, detached=("-d" in args), pass_env_file="-e" in args)
            elif (docker_op == 'push'):
                helpyItself.docker_push()
            elif (docker_op == 'prune'):
                helpyItself.docker_system_prune()
            else:
                printout(func="helpy", msg=f"Unknown option for [helpy.py docker]: '{docker_op}'. Check out [helpy.py help] for more information")
        elif (cmd1 == 'package'):
            package_op = pop_arg_or_exit(arglist=args, errormessage="[helpy.py package] requires another argument. Check out [helpy.py help] for more information")

            if (package_op == 'build'):
                #
                helpyItself.ensure_package_installed(package_name='twine')
                helpyItself.pip_freeze()
                helpyItself.package_build()
            elif (package_op == 'push'):
                helpyItself.ensure_package_installed(package_name='twine')
                helpyItself.package_push()
            else:
                printout(func="helpy", msg=f"Unknown option for [helpy.py package]: '{package_op}'. Check out [helpy.py help] for more information")
        elif (cmd1 == 'pip'):
            pip_op = pop_arg_or_exit(arglist=args, errormessage="[helpy.py package] requires another argument. Check out [helpy.py help] for more information")
            if (pip_op == 'install'):

                if ('requirements.txt' in " ".join(args)):
                    helpyItself.install_requirements_txt()
                else:
                    # 2. Package name should be set or taken from input
                    if (len(args) <= 0):
                        printout(func="tip", msg="you can also provide the package like python helpy.py pip install [packagename]", doPrint=True)
                        args = [input("Install which package?")]

                    helpyItself.install_package(package_names=args)
            elif (pip_op == 'upgrade' or pip_op == 'update'):
                if (len(args) <= 0):
                    printout(func="tip", msg="you can also provide the package like python helpy.py pip install [packagename]", doPrint=True)
                    args = [input(f"{pip_op} which package?")]
                helpyItself.install_package(package_names=args, upgrade=True)
            elif (pip_op == 'freeze'):
                #
                helpyItself.pip_freeze()
            else:
                #
                printout(func="helpy", msg=f"Unknown option for [helpy.py pip]: '{pip_op}'. Check out [helpy.py help] for more information")
        elif (cmd1 == 'test'):

            add_html = '--no-coverage' not in args
            if (add_html):
                helpyItself.ensure_package_installed(package_name='coverage')
            helpyItself.coveragetest(add_html=add_html)

        else:
            print(f"unknown command: '{cmd1}'")
            helpyItself.helpy_help()


# 2022-04-19 13:42
if __name__ == "__main__":
    main()