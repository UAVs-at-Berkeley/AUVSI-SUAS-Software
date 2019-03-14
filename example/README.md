
# Communication Server

## Flask Server
This application uses python flask module which is a framework for creating web apps. You will need to first create a virtual environment and install all the packages needed
```
virtualenv venv
source venv/bin/activate
pip install flask
pip install flask_sqlalchemy
pip install flask_migrate
pip install flask_wtf
```

## Setup 
Flask requires the environment variable to be set so it knows how to import it. 
```
export FLASK_APP=example.py
```

## Initializing 
Need to initialize the database before running. In addition, if the models.py is ever changed, must migrate the differences and upgrade the db.

```
flask db init
flask db migrate
flask db upgrade
flask run
```
