# Musika
Holds all the metadata for the music collections and compilations that I have; Exposes stats that are extensible; Used as a vehicle to learn the Django web framework.

## Run Locally on Docker

Prerequisite
- Docker installed 
- Set up the following environment variables:
  - SPOTIPY_CLIENT_ID
  - SPOTIPY_CLIENT_SECRET
  - SPOTIPY_REDIRECT_URI

1. build the app on docker 
``` docker compose up -d --build ```
2. Run the migrations
``` docker compose exec web python manage.py makemigrations ```
``` docker compose exec web python manage.py migrate ```
3. Ingest collections 
``` docker compose exec web python scripts/ingest_all_collections.py --clear ```

Application is then available on `http://127.0.0.1:8000/lib`

If the app asks you for the redirect url then you should run it first outside docker 
and provide it from copy/paste the open window; I don't know yet how to allow docker to open url's on the host


## Local Scripts 
1. Sync files with spotify `sync_spotify_collections.py` to get latest collections from remote
2. Then clean the liked playlist `prune_spotify_liked_playlist.py` to clear songs that may now be in a playlist
3. Then run the `ingest_all_collections.py` script

## Visualise 
Create a model graph 
From within a musika venv run
* ``` python3 manage.py graph_models musik_lib -o db.dot ```
Copy the contents into memory 
* ``` pbcopy < db.dot ```
Open a [visualize tool](https://dreampuf.github.io/GraphvizOnline/) , copy content, and look at graph 

Current 
![alt text](models.png "models")

## Test

After installing the app (See run locally), run
``` docker-compose exec web python manage.py test ```

## Heroku - Not Active 

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

