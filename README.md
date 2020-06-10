# Musika
Holds all the metadata for the music collections and compilations that I have; Exposes stats that are extensible; Used as a vehicle to learn the Django web framework.

## Run Locally

1. Install the app
``` pip install -e . [dev] ```

2. Run the migrations
``` python manage.py migrations ```


## Use with a DB

The application is configured to run with postgres DB;

I have used homebrew to install postgress sql - ``` brew install postgresql ```
and then followed [this tutorial](http://www.marinamele.com/taskbuster-django-tutorial/install-and-configure-posgresql-for-django) for setting it up;

I then defined several env vars; namely ``` MUSIKA_DB_NAME, MUSIKA_DB_USER, MUSIKA_DB_PASSWORD, MUSIKA_DB_HOST```

## Test

After installing the app (See run locally), run
``` python manage.py test ```

## Application

### Goal
The target state for the first development phase is to have all my compilations available on the webserver,
being able to navigate in between collections to songs to artists. Importantly, the application will expose interesting facts about the collections such as popular artists, popular genres, duplicate songs etc.
A more comprehensive list is available in [Development](Development.md)  - stats features.

