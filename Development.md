# The plan for development

## Milestones
### M0 - Setup

```Maria can see the homepage when she runs the app locally.```

Setup the Django framework and git. Set up index route.

### M1 - Library with first collection

```Maria can see the library, one collection, song and artist pages. They are all linkable.```

* Create the models and views and include one collection with basic info.
* Create Library page view.
* Create Collection page view.
* Create Track page view.
* Create Artist page view.

### M2 - Library with two collections and their stats

```Maria can see another collection and stats of the library and each the collections.```

Create the basic stats models and views. Link them to albums.

### M3 - Richer information on the library

```Maria can now see years of the songs, the albums, genres, times, and other fields. Stats have upgraded to include that too```

Provide tooling for scraping a 3rd party vendor for the information on songs.
Update models to include the required info.

### M4 - More collections are out

```Maria can now see the rest of the collection``

Improve and use the tooling to import and expose the rest of the library.


### M5 - Searchable library

```Maria can now search the library``

Implement search functionality in framework (Django) on each entity.


### M6 - Searchable library

```Maria can see really cool stats``

Add funkier stats for library and collections.


### M7 - Artists on the outside world

```Maria can now see web pages (Wiki?) for artists``

Augment admin tooling to link to wiki pages.



## Glossary

- *Library* - The entire collection of music Collections.
- *Collection* - A collection of music Tracks.
- *Track* - A music track associated with Artists.
- *Artist* - Composer of music track.
