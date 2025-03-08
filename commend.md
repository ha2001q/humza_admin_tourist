# [staticfile]
`python manage.py collectstatic`


## from terminal
1. `cd core`
2. `python manage.py makemigrations`
3. `python manage.py migrate`
4. `python manage.py createsuperuser`

# [Ubuntu Setup]
#### **Create venv for first time**
- `python -m venv venv`
#### **active venv**
- `source venv/bin/activate`
#### **install requierments**
 - `pip install -r requirements.txt`
#### **run project**
 - `python manage.py runserver`

# [Windows Setup]
#### **Create venv for first time**
- `python -m venv venv`
#### **active venv**
- `venv/Scripts/activate`
#### **install requierments**
 - `pip install -r requirements.txt`
#### **run project**
 - `python manage.py runserver`

-------
# [UvicornServer]
`uvicorn core.asgi:application --port 8000 --workers 4 --log-level debug --reload`
