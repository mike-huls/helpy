import random
import time
from dataclasses import dataclass, asdict
import os
import shutil
import sys
import subprocess
import importlib.util
import urllib.request
from functools import wraps
from typing import Callable



@dataclass
class HelpySettings:
    project_dir:str = os.getcwd()
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
                printout(func=".helyp", msg="PyPiUrl invalid: please provide pypi url without 'www.', 'http://' or 'https://' in .helpy", doPrint=True)

        if (self.venv_location == None):
            printout(func=".helyp", msg="VENV_LOCATION invalid: please provide your env file in .helpy", doPrint=True)
            quit()
        else:
            if (not os.path.isfile(self.python_location)):
                printout(func=".helyp", msg=f"Provided venv path ('{self.python_location}') is invalid: python.exe not found. \n Please initialize venv.", doPrint=True)
                quit()


class Dependencies:

    verbose:bool
    __helpy_settings:HelpySettings

    def __init__(self, helpy_settings:HelpySettings, verbose:bool=False):
        self.verbose = verbose
        self.__helpy_settings = helpy_settings

    def ensure_package_installed(self, package_name: str, import_package_name:str=None):
        if (not self.package_is_installed(package_name=package_name) and not self.package_is_installed(import_package_name)):
            if (input(f"Package '{package_name}' is not installed. \n"
                  f"  (venv location: {self.__helpy_settings.python_location})\n"
                  f"  pip install {package_name}? (y/n)".lower()
            ) != 'y'):
                printout(func=f"{Dependencies.__name__}.{self.ensure_package_installed.__name__}.", msg=f"Exiting..", doPrint=True)
                quit()
            self.install_package(package_names=[package_name])
    def package_is_installed(self, package_name:str=None) -> bool:
        """ Returns t/f depending on whether a package is installed in this project
            :arg package_name   str     name of the package you're checking
        """
        if (package_name == None):
            return False
        return importlib.util.find_spec(package_name) != None
    def install_package(self, package_names:[str], install_globally:bool=False) -> None:
        """ Wrapper around pip install """

        # 1. Add extra-index-url?
        extra_index_url = ""
        if (self.__helpy_settings.pypi_url != None and self.__helpy_settings.pypi_url != None and self.__helpy_settings.pypi_url != None):
            extra_index_url = f"--extra-index-url https://{self.__helpy_settings.pypi_username}:{self.__helpy_settings.pypi_password}@{self.__helpy_settings.pypi_url}"

        # 2. Create and execute install command
        cmd_install: str = f"pip install {extra_index_url} {' '.join(package_names)} --upgrade"
        if (not install_globally):
            cmd_install = f"{self.__helpy_settings.python_location} -m" + cmd_install
        # cmd_install: str = f"{self.helpy_settings.python_location} -m pip install {extra_index_url} {' '.join(package_names)} --upgrade"
        print(cmd_install)
        quit()
        try:
            subprocess.check_output(cmd_install)
            printout(func=self.install_package.__name__, msg=f"Installed {package_names}", doPrint=True)
        except subprocess.CalledProcessError as e:
            printout(func=self.package_build.__name__, msg=f"Error building package: {e}", doPrint=self.verbose)
    def install_requirements_txt(self) -> None:
        """ """

        # 1. Does the requirments.txt file exits in the project dir?
        if (not os.path.isfile(os.path.join(self.__helpy_settings.project_dir, 'requirements.txt'))):
            printout(func=self.install_package.__name__, msg=f"requirements.txt does not exist", doPrint=True)
            quit()


        # 2. Add extra-index-url?
        extra_index_url = ""
        if (self.__helpy_settings.pypi_url != None and self.__helpy_settings.pypi_url != None and self.__helpy_settings.pypi_url != None):
            extra_index_url = f"--extra-index-url https://{self.__helpy_settings.pypi_username}:{self.__helpy_settings.pypi_password}@{self.__helpy_settings.pypi_url}"

        cmd_install: str = f"{self.__helpy_settings.python_location} -m pip install {extra_index_url} -r requirements.txt --upgrade"
        try:
            subprocess.check_output(cmd_install)
            printout(func=self.install_package.__name__, msg=f"Installed requirements.txt", doPrint=True)
        except subprocess.CalledProcessError as e:
            printout(func=self.package_build.__name__, msg=f"Error installing requirements.txt: {e}", doPrint=self.verbose)

    def package_build(self):
        """ packages code in current directory to the dist folder """

        # 1. Install required packages`
        self.ensure_package_installed('twine')

        # 2. Make sure there is an empty dist folder in the project root
        dist_folder_path = os.path.join(os.getcwd(), 'dist')
        if (os.path.isdir(dist_folder_path)):
            printout(func=self.package_build.__name__, msg=f"removing content of dist folder at {dist_folder_path}", doPrint=self.verbose)
            remove_folder(folderpath=dist_folder_path, verbose=False)
            create_folder(folderpath=dist_folder_path, verbose=False)
            printout(func=self.package_build.__name__, msg=f"removed content of dist folder at {dist_folder_path}", doPrint=self.verbose)

        # 3. Pip freeze dependencies
        self.pip_freeze()

        # 4 Call setup function
        setup_cmd = f"{self.__helpy_settings.python_location} setup.py sdist"
        try:
            subprocess.check_output(setup_cmd)
        except subprocess.CalledProcessError as e:
            printout(func=self.package_build.__name__, msg=f"Error building package: {e}", doPrint=self.verbose)
    def package_push(self, pypi_url: str, pypi_username: str, pypi_password: str, force:bool=False):
        """ Pushes the package to pypi server """

        # 1. Install required packages`
        self.ensure_package_installed('twine')

        # 2. Make sure we have the correct pypi url
        pypi_url = f'https://{pypi_url}'
        printout(func=f"{self.package_push.__name__}", msg=f"PyPi Url: {pypi_url}", doPrint=self.verbose)

        # 3. Prompt sure if required
        if (not force):
            if (input("Are you sure you want to push the package to PyPi? (y/n)").lower() != 'y'):
                return

        # 4.

        printout(func=self.package_push.__name__, msg=f"Pushing package to '{pypi_url}'", doPrint=self.verbose)
        try:
            cmd_push_package = f'{self.__helpy_settings.python_location} -m twine upload dist/* --repository-url "{pypi_url}" -u "{pypi_username}" -p "{pypi_password}"'
            subprocess.check_output(cmd_push_package)
            printout(func=self.package_push.__name__, msg=f"Successfully pushed package to '{pypi_url}'", doPrint=self.verbose)
        except Exception as e:
            printout(func=self.package_push.__name__, msg=f"Failed push package to '{pypi_url}': \n\t'{e}'", doPrint=True)
    def pip_freeze(self):
        printout(func=self.pip_freeze.__name__, msg=f"Pip freezing requirements..", doPrint=self.verbose)
        try:
            with open('requirements.txt', 'w') as file_:
                try:
                    subprocess.call([self.__helpy_settings.python_location, '-m', 'pip', 'freeze'], stdout=file_)
                except subprocess.CalledProcessError as e:
                    printout(func=self.package_build.__name__, msg=f"Error building package: {e}", doPrint=self.verbose)

            printout(func=self.pip_freeze.__name__, msg=f"Pip freeze requirements succes", doPrint=self.verbose)
        except Exception as e:
            printout(func=self.pip_freeze.__name__, msg=f"Pip freeze failed: \n\t'{e}'", doPrint=True)


class HelpyHelper:
    project_dir: str = os.getcwd()
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
    def init_helpy(self, project_folder: str):
        """ Initializes """

        printout(func=self.init_helpy.__name__, msg=f"Initializing helpy at {self.project_dir}..", doPrint=self.verbose)
        FILES_URL = f"https://raw.githubusercontent.com/mike-huls/helpy/main/files"

        # config/conf/.env
        create_folder(folderpath=os.path.join(project_folder, 'config'), verbose=self.verbose)
        create_folder(folderpath=os.path.join(project_folder, 'config', 'conf'), verbose=self.verbose)
        download_file(url=f"{FILES_URL}/default_env", filepath=os.path.join(project_folder, 'config', 'conf', '.env'), verbose=self.verbose, overwrite=self.force)
        download_file(url=f"{FILES_URL}/default_definitions.py", filepath=os.path.join(project_folder, 'config', 'definitions.py'), verbose=self.verbose, overwrite=self.force)

        # Create .helpy settings file
        download_file(url=f"{FILES_URL}/default_.helpy", filepath=os.path.join(self.project_dir, '.helpy'), verbose=self.verbose, overwrite=self.force)
        printout(func=self.init_helpy.__name__, msg=f"Initialized helpy. Don't forget to activate the new venv", doPrint=self.verbose)

    def init_project(self, project_folder: str, project_name: str = "My Project"):
        """ Needs certain files and folder structure always. """

        PROJFOLDER = os.getcwd()
        printout(func=self.init_project.__name__, msg=f"Initializing new project '{project_name}' at {PROJFOLDER}..", doPrint=self.verbose)
        FILES_URL = f"https://raw.githubusercontent.com/mike-huls/helpy/main/files"

        # config/conf/.env
        create_folder(folderpath=os.path.join(project_folder, 'config'), verbose=self.verbose)
        create_folder(folderpath=os.path.join(project_folder, 'config', 'conf'), verbose=self.verbose)
        download_file(url=f"{FILES_URL}/default_env", filepath=os.path.join(project_folder, 'config', 'conf', '.env'), verbose=self.verbose, overwrite=self.force)
        download_file(url=f"{FILES_URL}/default_definitions.py", filepath=os.path.join(project_folder, 'config', 'definitions.py'), verbose=self.verbose, overwrite=self.force)

        # Create venv
        # printout(func=self.init_project.__name__, msg=f"Initializing venv..", doPrint=self.verbose)
        # # create_virtualenv(projectfolder=PROJFOLDER, verbose=self.verbose)
        # printout(func=self.init_project.__name__, msg=f"Initialized venv", doPrint=self.verbose)

        # Create default folders
        create_folder(folderpath=os.path.join(PROJFOLDER, 'doc'), verbose=self.verbose)
        download_file(url=f"{FILES_URL}/default_doc.md", filepath=os.path.join(PROJFOLDER, 'doc', 'example.md'), verbose=self.verbose, overwrite=self.force)
        create_folder(folderpath=os.path.join(PROJFOLDER, 'test'), verbose=self.verbose)
        create_empty_file(filepath=os.path.join(PROJFOLDER, 'test', '__init__.py'), verbose=self.verbose)
        download_file(url=f"{FILES_URL}/default_test.py", filepath=os.path.join(PROJFOLDER, 'test', 'test_functions.py'), verbose=self.verbose, overwrite=self.force)

        # Create default files (with content)
        download_file(url=f"{FILES_URL}/default_gitignore", filepath=os.path.join(PROJFOLDER, '.gitignore'), verbose=self.verbose, overwrite=self.force)
        download_file(url=f"{FILES_URL}/default_readme_package.md", filepath=os.path.join(PROJFOLDER, 'readme.md'), verbose=self.verbose, overwrite=self.force)
        replace_in_file(filepath=os.path.join(PROJFOLDER, 'readme.md'), replace_this_text='{PROJECT_NAME}', replacment_text='My project')
        download_file(url=f"{FILES_URL}/default_main.py", filepath=os.path.join(PROJFOLDER, 'main.py'), verbose=self.verbose, overwrite=self.force)
        download_file(url=f"{FILES_URL}/default_Dockerfile", filepath=os.path.join(PROJFOLDER, 'Dockerfile'), verbose=self.verbose, overwrite=self.force)
        download_file(url=f"{FILES_URL}/default_dockerignore", filepath=os.path.join(PROJFOLDER, '.dockerignore'), verbose=self.verbose, overwrite=self.force)

        printout(func=self.init_project.__name__, msg=f"Project initialized", doPrint=True)

    def init_package(self, package_name: str):
        """ Get files and folder structure"""
        PROJFOLDER = os.getcwd()
        printout(func=self.init_project.__name__, msg=f"Initializing new project at {PROJFOLDER}..", doPrint=self.verbose)
        FILES_URL = f"https://raw.githubusercontent.com/mike-huls/helpy/main/files"

        # # Create venv
        # printout(func=self.init_package.__name__, msg=f"Initializing venv..", doPrint=self.verbose)
        # # create_virtualenv(projectfolder=PROJFOLDER, verbose=self.verbose)
        # printout(func=self.init_package.__name__, msg=f"Initialized venv", doPrint=self.verbose)

        # # config/conf/.env
        # create_folder(folderpath=os.path.join(PROJFOLDER, 'config'), verbose=self.verbose)
        # create_folder(folderpath=os.path.join(PROJFOLDER, 'config', 'conf'), verbose=self.verbose)
        # download_file(url=f"{FILES_URL}/default_env", filepath=os.path.join(PROJFOLDER, 'config', 'conf', '.env'), verbose=self.verbose, overwrite=self.force)
        # download_file(url=f"{FILES_URL}/default_definitions.py", filepath=os.path.join(PROJFOLDER, 'config', 'definitions.py'), verbose=self.verbose, overwrite=self.force)

        # Create default folders
        create_folder(folderpath=os.path.join(PROJFOLDER, 'doc'), verbose=self.verbose)
        download_file(url=f"{FILES_URL}/default_doc.md", filepath=os.path.join(PROJFOLDER, 'doc', 'example.md'), verbose=self.verbose, overwrite=self.force)
        create_folder(folderpath=os.path.join(PROJFOLDER, 'test'), verbose=self.verbose)
        create_empty_file(filepath=os.path.join(PROJFOLDER, 'test', '__init__.py'), verbose=self.verbose)
        download_file(url=f"{FILES_URL}/default_test.py", filepath=os.path.join(PROJFOLDER, 'test', 'test_functions.py'), verbose=self.verbose, overwrite=self.force)

        # Create default files (with content)
        download_file(url=f"{FILES_URL}/default_gitignore", filepath=os.path.join(PROJFOLDER, '.gitignore'), verbose=self.verbose, overwrite=self.force)
        download_file(url=f"{FILES_URL}/default_readme_package.md", filepath=os.path.join(PROJFOLDER, 'readme.md'), verbose=self.verbose, overwrite=self.force)
        replace_in_file(filepath=os.path.join(PROJFOLDER, 'readme.md'), replace_this_text='{PROJECT_NAME}', replacment_text=package_name)
        download_file(url=f"{FILES_URL}/default_setup.cfg", filepath=os.path.join(PROJFOLDER, 'setup.cfg'), verbose=self.verbose, overwrite=self.force)
        download_file(url=f"{FILES_URL}/default_setup.py", filepath=os.path.join(PROJFOLDER, 'setup.py'), verbose=self.verbose, overwrite=self.force)
        replace_in_file(filepath=os.path.join(PROJFOLDER, 'setup.py'), replace_this_text='{PROJECT_NAME}', replacment_text=package_name)

        # Create module folder with __init__.py
        create_folder(folderpath=os.path.join(PROJFOLDER, package_name), verbose=self.verbose)
        create_empty_file(filepath=os.path.join(PROJFOLDER, package_name, '__init__.py'), verbose=self.verbose)

        printout(func=self.init_package.__name__, msg=f"Project initialized", doPrint=True)

    # Loading .helpy and .env
    def read_helpy_settings(self) -> HelpySettings:
        """ """

        # 1. Ensure helpy is initialized?
        self.__ensure_helpy_init()

        # 2. Read the .helpy file
        helpysettings_path = os.path.join(self.project_dir, '.helpy')

        # 3. Read .helpy into a dict after cleaning. Then load the dict into a HelpySettings instance
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
        helpySettings = HelpySettings(**helpySettingsDict)

        # 4. Get the path to the env file path from .helpy and load the env file
        env_file_path: str
        if ('${' in "".join(helpySettings_lines)):
            envfullpath = os.path.join(helpySettings.project_dir, helpySettings.env_file_path)



            if (helpySettings.env_file_path == None):
                printout(
                    func=f"{self.read_helpy_settings.__name__}",
                    msg=f"You specified keys in .helpy that take values from and .env file but the path to the .env file is not specified in .helpy\n"
                        f"Please provide a value for key ENV_FILE_PATH in .helpy\n"
                        f"Exiting..", doPrint=True)
                quit()
            else:
                # check if the .env actually exists
                if (not os.path.isfile(envfullpath)):
                    printout(
                        func=f"{self.read_helpy_settings.__name__}",
                        msg=f"The .env file you specified in .helpy does not exist\n"
                            f"Please create a .env file at {envfullpath}\n"
                            f"Exiting..", doPrint=True)
                    quit()
            # if (helpySettings.env_file_path)
            env_file_path = os.path.join(self.project_dir, helpySettings.env_file_path)
            self.load_env_file(env_file_path=env_file_path)

        # 5. Replace ${variables} in helpySettings with values from env var is specified
        # helpySettingsDict = asdict(helpySettings)
        for k, v in helpySettingsDict.items():
            if (v == '' or v == None):
                continue
            if (v[:2] == '${'):
                envfileVal = os.environ.get(v[2:-1])  # gets rid of ${ ... }
                if (envfileVal == None):
                    printout(func=f"{self.read_helpy_settings.__name__}", msg=f"You specified a key in .helpy that cannot be found in your .env.\n"
                                                                              f"Please check if key '{v[2:-1]}' exists in the .env at {env_file_path})\n"
                                                                              f"Exiting..", doPrint=True)
                helpySettingsDict[k] = envfileVal

        return HelpySettings(**helpySettingsDict)

    def load_env_file(self, env_file_path: str) -> None:
        """ Loads the values from the specified env_file into the environment """

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
                os.environ[k] = v

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
                printout(func=self.update.__name__, msg="Helpy is up to date", doPrint=True)
                return
            else:
                if (input("Update available! Update? (y/n)").lower() != 'y'):
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

        helpySettings: HelpySettings = self.read_helpy_settings()

        # for k in fields(HelpyHelper)
        print(
            f"""HELPY version {self.helpy_cur_version()}

        ENVIRONMENT
        VENV_LOCATION: \t {helpySettings.venv_location}
        ENV_FILE_PATH: \t {helpySettings.env_file_path}

        PYPI:
        PYPI URL: \t {helpySettings.pypi_url if (helpySettings.pypi_url) else ""}
        PYPI username: \t {helpySettings.pypi_username if (helpySettings.pypi_username) else ""}
        PYPI password: \t {"*" * len(helpySettings.pypi_password) if (helpySettings.pypi_password) else ""}

        DOCKER:
        image name: \t {helpySettings.docker_image_name if (helpySettings.docker_image_name) else ""}
        """)

    def help(self):
        helpmessage = f"""
        Welcome to Helpy (v.{self.helpy_cur_version()})
        Call [python helpy.py] with any of the following commands:
            help                            display this message
            info                            displays information about helpy, including constants you've set
            version                         displays information about the current version of helpy 
            update                          updates helpy if there is a new version
            init project                    prepares the current folder for a python project
            init package                    prepares the current folder for a python package
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

    # Venv
    # def create_virtualenv(self):
    #     """ Creates a virtual environment in a project folder """
    #     helpySettings:HelpySettings = self.read_helpy_settings()
    #
    #     if (os.path.exists(os.path.join(self.project_dir, 'venv'))):
    #         printout(func=self.create_virtualenv.__name__, msg=f"Virtual environment already exists", doPrint=self.verbose)
    #         return
    #
    #     install_package_globally(package_name='virtualenv', import_package_name='venv', prompt_sure=True, verbose=verbose)
    #     printout(func=self.create_virtualenv.__name__, msg=f"Installing virtualenv", doPrint=verbose)
    #     subprocess.call(f'python.exe -m venv {projectfolder}/venv')
    #     printout(func=self.create_virtualenv.__name__, msg=f"Successfully created virtualenv", doPrint=verbose)


# region UTIL
def prompt_yes(promptmessage:str) -> bool:
    return input(promptmessage).lower().strip() == 'y'
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
# endregion

""" 
        if (os.path.exists(os.path.join(self.project_dir, 'venv'))):
            printout(func=self.create_virtualenv.__name__, msg=f"Virtual environment already exists", doPrint=self.verbose)
            return

        install_package_globally(package_name='virtualenv', import_package_name='venv', prompt_sure=True, verbose=verbose)
        printout(func=self.create_virtualenv.__name__, msg=f"Installing virtualenv", doPrint=verbose)
        subprocess.call(f'python.exe -m venv {projectfolder}/venv')
        printout(func=self.create_virtualenv.__name__, msg=f"Successfully created virtualenv", doPrint=verbose)

"""
# region SERVE
def serve_fastapi(python_location:str, env_file_location:str, verbose:bool=False):
    """ Makes it so that you can serve fastapi"""

    # 1. Ensure Fastapi is installed
    env_file_add = f"--env-file {env_file_location}" if (env_file_location) else ""
    cmd_serve = f'{python_location} -m uvicorn main:app {env_file_add} --reload'
    try:
        subprocess.check_output(cmd_serve)
    except subprocess.CalledProcessError as e:
        printout(func=serve_fastapi.__name__, msg=f"Error building package: {e}", doPrint=verbose)
# endregion

# region DOCKER
def docker_system_prune():
    try:
        subprocess.call(f"docker system prune -f")
    except Exception as e:
        printout(func=docker_system_prune.__name__, msg=f"Docker system prune failed: \t\n'{e}'", doPrint=True)
def docker_build(docker_image_name:str, verbose: bool = False):
    if (docker_image_name == None or len(docker_image_name) < 3):
        printout(func=docker_build.__name__, msg="Please provide a docker image name in .helpy", doPrint=True)
        quit()
    printout(func=docker_build.__name__, msg=f"Building docker image '{docker_image_name}'..", doPrint=verbose)
    try:
        subprocess.call(f'docker build . -t "{docker_image_name}" --secret id=pypi_creds,src=config\conf\.env')
        docker_system_prune()
        printout(func=docker_build.__name__, msg=f"Successfully built docker image", doPrint=verbose)
    except Exception as e:
        printout(func=docker_build.__name__, msg=f"Failed to build docker image: \n\t'{e}", doPrint=True)
def docker_push(docker_image_name:str, verbose: bool = False, force: bool = False):
    """ Pushes the docker image to the docker hub """

    if (len(docker_image_name) <= 3):
        printout(func=docker_push.__name__, msg=f"Invalid DOCKER_IMAGE_NAME: '{docker_image_name}'. Please provide a docker image name in helpy.py", doPrint=True)
        return

    if (not force):
        if (input(f"Are you sure you want to push '{docker_image_name}' to dockerhub? (y/n)").lower() != "y"):
            return

    printout(func=docker_push.__name__, msg=f"Pushing image '{docker_image_name}' to docker hub", doPrint=verbose)
    try:
        subprocess.call(f'docker push "{docker_image_name}"')
        printout(func=docker_push.__name__, msg=f"Successfully pushed image '{docker_image_name}' to docker hub", doPrint=verbose)
    except Exception as e:
        printout(func=docker_push.__name__, msg=f"Failed to push docker image: \n\t'{e}'", doPrint=True)
# endregion

#region UNIITEST + COVERAGE
def coveragetest(add_html:bool=True, verbose:bool=False, force:bool=False):
    """ Creates coveragetest """

    cmd = f"""coverage run -m unittest discover"""
    if (add_html):
        cmd += """ && coverage html --omit="*/test*"""
    subprocess.call(cmd)
#endregion



def main():
    """ Parse command line """
    args = sys.argv[1:]


    # Preferences
    DO_FORCE = '-f' in args
    args.remove('-f') if ('-f' in args) else None
    VERBOSE = '-v' in args
    args.remove('-v') if ('-v' in args) else None


    # Init HELPY
    print("check if .env exists")

    helpyHelper = HelpyHelper(verbose=VERBOSE, force=DO_FORCE)  # Inits helpy and loads the settings (and optionally the .env file) and validate
    helpy_settings:HelpySettings = helpyHelper.read_helpy_settings()
    helpy_settings.validate()

    print("venv?")
    print(os.path.exists(os.path.join(helpy_settings.project_dir, 'venv')))


    # Helpers
    deps = Dependencies(helpy_settings=helpy_settings, verbose=VERBOSE)

    # Create venv
    if (not os.path.exists(os.path.join(helpy_settings.project_dir, 'venv'))):
        printout(func=main.__name__, msg=f"No venv detected", doPrint=VERBOSE)

    quit()
    # Create venv
    if (not os.path.exists(os.path.join(helpy_settings.project_dir, 'venv'))):
        printout(func=main.__name__, msg=f"No venv detected", doPrint=VERBOSE)
        deps.install_package(package_names='virtualenv', install_globally=True)


    # Parse arguments
    # Must provide at least one argument
    if (len(args) == 0):
        help()
        quit()
    cmd1 = pop_arg_or_exit(arglist=args, errormessage="Helpy expects at least one argument. Check out [helpy.py help] for more information")





    # Check for updates
    if (cmd1 != 'update'):
        # Checks for updates
        helpyHelper.update()

    # HELPY functions
    if (cmd1 == 'update'):
        #
        helpyHelper.update()
    elif (cmd1 == 'help'):
        #
        helpyHelper.help()
    elif (cmd1 == 'info'):
        #
        helpyHelper.display_info()
    elif (cmd1 == 'version'):
        #
        print(f"Helpy version {helpyHelper.helpy_cur_version()}")



    # Regular functions
    elif (cmd1 == 'init'):
        # Get init_type
        init_type = pop_arg_or_exit(arglist=args, errormessage="[helpy.py init] requires another argument. Check out [helpy.py help] for more information")


        # Functions
        if (init_type == 'helpy'):
            #
            helpyHelper.init_helpy(helpy_settings.project_dir)
        elif (init_type == 'project'):
            project_name = args[0] if (len(args) > 0) else None
            if (project_name == None):
                project_name = input("Project name?")
            helpyHelper.init_project(project_name=project_name, project_folder=helpy_settings.project_dir)
        elif (init_type == 'package'):
            package_name = args[0] if (len(args) > 0) else None
            if (package_name == None):
                package_name = input("What is this package called?")
            helpyHelper.init_package(package_name=package_name, project_folder=helpy_settings.project_dir)
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
            deps.ensure_package_installed(package_name='fastapi')
            deps.ensure_package_installed(package_name='uvicorn')
            serve_fastapi(python_location=helpy_settings.python_location, env_file_location=helpy_settings.env_file_path, verbose=VERBOSE)
        else:
            printout(func="helpy", msg=f"Unknown option for [helpy.py serve]: '{serve_op}'. Check out [helpy.py serve list] for more information")
    elif (cmd1 == 'docker'):
        docker_op = pop_arg_or_exit(arglist=args, errormessage="[helpy.py docker] requires another argument. Check out [helpy.py help] for more information")
        if (docker_op == 'build'):
            deps.pip_freeze()
            docker_build(docker_image_name=helpy_settings.docker_image_name, verbose=VERBOSE)
        elif (docker_op == 'push'):
            docker_push(docker_image_name=helpy_settings.docker_image_name, force=DO_FORCE, verbose=VERBOSE)
        else:
            printout(func="helpy", msg=f"Unknown option for [helpy.py docker]: '{docker_op}'. Check out [helpy.py help] for more information")
    elif (cmd1 == 'package'):
        package_op = pop_arg_or_exit(arglist=args, errormessage="[helpy.py package] requires another argument. Check out [helpy.py help] for more information")

        if (package_op == 'build'):
            #
            deps.ensure_package_installed(package_name='twine')
            deps.pip_freeze()
            deps.package_build()
        elif (package_op == 'push'):

            # 1. Check if all variables are set
            if (len(str(helpy_settings.pypi_url)) <= 5):
                printout(func="push", msg="Please set PyPi Url in .helpy")
                sys.exit(0)
            if (len(str(helpy_settings.pypi_username)) <= 5):
                printout(func="push", msg="Please set PyPi Username in .helpy")
                sys.exit(0)
            if (len(str(helpy_settings.pypi_password)) <= 5):
                printout(func="push", msg="Please set PyPi Password in .helpy")
                sys.exit(0)
            deps.package_push(pypi_url=helpy_settings.pypi_url, pypi_username=helpy_settings.pypi_username, pypi_password=helpy_settings.pypi_password)
        else:
            printout(func="helpy", msg=f"Unknown option for [helpy.py package]: '{package_op}'. Check out [helpy.py help] for more information")
    elif (cmd1 == 'pip'):

        pip_op = pop_arg_or_exit(arglist=args, errormessage="[helpy.py package] requires another argument. Check out [helpy.py help] for more information")
        if (pip_op == 'install'):


            if ('requirements.txt' in " ".join(args)):
                deps.install_requirements_txt()
            else:
                # 2. Package name should be set or taken from input
                if (len(args) <= 0):
                    printout(func="tip", msg="you can also provide the package like python helpy.py pip install [packagename]", doPrint=True)
                    args = [input("Install which package?")]

                deps.install_package(package_names=args)
        elif (pip_op == 'upgrade' or pip_op == 'update'):
            if (len(args) <= 0):
                printout(func="tip", msg="you can also provide the package like python helpy.py pip install [packagename]", doPrint=True)
                args = [input(f"{pip_op} which package?")]
            deps.install_package(package_names=args)
        elif (pip_op == 'freeze'):
            #
            deps.pip_freeze()
        else:
            #
            printout(func="helpy", msg=f"Unknown option for [helpy.py pip]: '{pip_op}'. Check out [helpy.py help] for more information")

    elif (cmd1 == 'test'):

        deps.ensure_package_installed(package_name='coverage')
        add_html = '--no-coverage' not in args
        coveragetest(add_html=add_html)

    else:
        print(f"unknown command: '{cmd1}'")
        help()


# 2022-03-23 16:52
if __name__ == "__main__":

    main()