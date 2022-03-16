# helpy
Helps to initialize python projects. 

testing mermaid:
```mermaid
    graph TD
    A[Christmas] -->|Get money| B(Go shopping)
    B --> C{Let me think}
    C -->|One| D[Laptop]
    C -->|Two| E[iPhone]
    C -->|Three| F[fa:fa-car Car]
```


### Functionalities
check out `python helpy.py help`. Other arguments:
```yaml
help                           display this message
info                           displays information about helpy, including constants you've set
version                        displays information about the current version of helpy 
update                         updates helpy if there is a new version

init project                   prepares the current folder for a python project
init package                   prepares the current folder for a python package

serve [type]                   tries to spin up the current project as a fastapi project
serve list                     display a list of all types of applications you can serve

docker build                   builds the image specified in the dockerfile
docker push                    pushes the image to dockerhub. Set username in .env or from cmd

package build                  uses the setup.py to build the package
package push                   pushes the package to the pypi specified in the .env

pip install [packagename]      installes a package using pypi OR the pypi specified in helpy (PYPI_URL)
pip install requirements.txt   installs a requirements.txt file using pypi OR the pypi specified in the helpy (PYPI_URL)
pip freeze                     freezes all dependencies in a requirements.txt
```

