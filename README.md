# Label Toolkit Backend
This project serves as a very slim backend designed to work with the web-based Label Toolkit application in order to demonstrate proper use of my works. This server receives uploading streaming requests issued by the app and processes with certain analysis.

The server is set up with Django and MariaDB.

## Running the server
If you wish to run the server, the first step is installing Python@3.7.9. 

You can also create a virtual environmnet for this project.
```
python3 -m venv venv
source venv/bin/activate
```

Once that's out of the way, open a terminal and run the following command:
```
pip install -r requirements.txt
```
to install required packages.

Next, set up your own database. MariaDB is used in this project.

The server is now ready to run. Simply point a terminal to the project's folder and run:
```
python manage.py runserver
```

which should result in output such as:
```
System check identified no issues (0 silenced).
January 06, 2021 - 08:20:12
Django version 3.1, using settings 'backend.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

## Using your credentials
Use your own credentials by setting the `SECRET_KEY` and `DATABASE_URL` environment variables before running the server.
```
### .env ###
SECRET_KEY=my_secret_key
DATABASE_URL=mysql://{username}:{pwd}@localhost:3306/{dbname}?charset=utf8mb4
```



