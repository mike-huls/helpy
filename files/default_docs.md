# Examples

serve
```commandline
venv/Scripts/python.exe -m uvicorn main:app --env-file config/conf/.env --reload
```

docker build
```commandline
venv/Scripts/python.exe -m pip freeze > requirements.txt
docker build . -t "$DOCKERHUB/$PROJECT/$APP"
docker system prune -f
```

docker push
```commandline
docker login $DOCKERHUB
docker push "$DOCKERHUB/$PROJECT/$APP"
```

pip freeze 
```commandline
venv/scripts/python.exe -m pip freeze | grep -v 'pyodbc' > requirements.txt
```

pypi build package
```commandline
rm ./dist/*
venv/scripts/python.exe -m pip freeze > requirements.txt;
venv/scripts/python.exe -m pip install twine --upgrade;
venv/scripts/python.exe setup.py sdist;
```

pypi push package
```commandline
venv/scripts/python.exe -m twine upload dist/* --repository-url "$PYPI_URL" -u "$USERNAME" -p [yourpasswordhere];
```