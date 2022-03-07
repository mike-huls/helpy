# helpy
Helps to initialize python projects. 

### Functionalities
check out `python helpy.py help`
```yaml
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
```
