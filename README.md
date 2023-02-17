# Minerva
Inventory Manager

### Configuration
config.toml specifies project parameters and dependencies, as well as the API framework. The latter aspect will most likely be discontinued as the project matures, as it originally enabled the fresh construction of a barebones flask app, an action which we will have no need of performing going forward.

The parameters, such as host, port, and base docker image, and the python dependencies, such as gunicorn and of course flask, will however continue to be recorded in this file. Should they be tweaked, run the following (at the root directory of Minerva) to update requirements.txt, Dockerfile, and server_ctl:

`python tools/mk_flask.py -c config.toml -w src artifacts`

This is an idempotent operation. Note that this command will produce a virtual environment in the directory if one is not already present. Finally, git is poised to overlook .venv and server_ctl, but will take notice of Dockerfile and requirements.txt.

### Starting application
#### server_ctl
Depending on the operating system, either server_ctl or server_ctl.py will be placed in the root directory after running the command above. Simply run this file as an executable and it will takeoff.

#### Docker
Once in Minerva, follow the usual sequence:

`docker build -t minerva .`

`docker run -dp {PORT}:{PORT} minerva`

where PORT is whatever port number is exposed in the Dockerfile.
