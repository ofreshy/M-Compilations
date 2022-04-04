# Musika
Holds all the metadata for the music collections and compilations that I have; Exposes stats that are extensible; Used as a vehicle to learn the Django web framework.

## Run Locally

1. Install the app
``` pip install -e . [dev] ```
2. Run the migrations
``` python manage.py migrate ```
3. Run the server with 
``` python manage.py runserver ```

Application is then available on `http://127.0.0.1:8000/lib`

## Use with a DB

The application is configured to run with postgres DB;

I have used homebrew to install postgress sql - ``` brew install postgresql ```
and then followed [this tutorial](http://www.marinamele.com/taskbuster-django-tutorial/install-and-configure-posgresql-for-django) for setting it up;

I then defined several env vars; namely ``` MUSIKA_DB_NAME, MUSIKA_DB_USER, MUSIKA_DB_PASSWORD, MUSIKA_DB_HOST```

## Test

After installing the app (See run locally), run
``` python manage.py test ```

## Heroku

The application is currently running on Heroku - https://musika-3.herokuapp.com/lib/

Created the app on heroku; See that you need to have all data on master
* ``` heroku create musika-3 ```
* Then adding ``` 'musika-3.herokuapp.com', 'localhost', '127.0.0.1' ``` to allowed hosts in settings.py;
* ``` heroku config:set DISABLE_COLLECTSTATIC=1 ```
* ``` git push heroku master ```

Took the following values from the heroku postgres settings page
* ``` heroku config:set MUSIKA_DB_NAME=*** ```
* ``` heroku config:set MUSIKA_DB_USER=*** ```
* ``` heroku config:set MUSIKA_DB_PASSWORD=*** ```
* ``` heroku config:set MUSIKA_DB_HOST=*** ```
* ``` heroku config ```  to verify  the current config vars

Add migrations and create super user
* ``` heroku run python manage.py migrate ```
* ``` heroku run python manage.py createsuperuser ```

Seed the DB
* ``` heroku config:set DJANGO_SETTINGS_MODULE=musika.settings ```
* ``` heroku run python scripts/ingest_collections.py all ```

### Goal
The target state for the first development phase is to have all my compilations available on the webserver,
being able to navigate in between collections to songs to artists. Importantly, the application will expose interesting facts about the collections such as popular artists, popular genres, duplicate songs etc.
A more comprehensive list is available in [Development](Development.md)  - stats features.

