Reimplementation of the old [Avenida Minion](old.md).
The old codebase was too coupled to Avenida's needs so I rewrited it from scratch using Django, Django Rest Framework and Docker.

Minion aims to help you to set up development and testing environments running several microservices. It provides a control panel where you can see which services and versions and running. You can also build branches and tags on demand.

Given a git repository Minion will build Docker images using the Dockerfile in the root directory. You can configure the environment variables, ports and volumes that containers will use.

A live demo is available at http://minion.manuelcarrizo.com

## Running

Minion needs to be run by an user that has permissions to run docker commands, a git client is also needed

```
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py runserver
```
