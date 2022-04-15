# helpy
Helps to initialize python projects. 


### Functionalities
check out `python helpy.py help`. Other arguments:
```yaml
help                            display this message
info                            displays information about helpy, including constants you've set
version                         displays information about the current version of helpy 
update                          updates helpy if there is a new version
create venv                     Creates a virtualenv

init project                    prepares the current folder for a python project
init package                    prepares the current folder for a python package
init fastapi                    prepares the current folder for a FastAPI project

serve fastapi                   tries to spin up the current project as a fastapi project (-p PORT) 

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
```

