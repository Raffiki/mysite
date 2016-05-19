# application manager
manage applications, django style


## requirements

### dependencies

- `pip install requirements.txt`

### authentication

authentication is provided through Twitter OAuth2 api

- Get your lan IP: let's say it's `192.168.0.22`
- Create a Twitter app: https://apps.twitter.com/app
    - in Settings/Website, put: http://192.168.0.22:8000/login
    - in Settings/Callback URL, put: http://192.168.0.22:8000/login/authenticated
    - in Keys and Access Tokens, get Key & secret
- Create environment variables:
    - TWITTER_TOKEN=Key
    - TWITTER_SECRET=secret
    
## usage

- `python manage.py migrate`
- `python manage.py runserver 192.168.0.22:8000`

## tests

app is written and tested with Python `3.5.1`

Run tests with `python manage.py test`

## docs

Cfr. Readme + [tests](apps/tests.py)
