![Yamdb workflow](https://github.com/selectcoma/yamdb_final/actions/workflows/yamdb_workflow/badge.svg)


**API for YAMDB service**

*Important URLS:*
- Documentation `178.154.198.217/redoc`
- API `178.154.198.217/api/v1`
- Admin site `178.154.198.217/admin`

YAMDB collects user reviews for different  categories of items like books, movies, music, etc.

This app was developped using django and django-rest-framework. Postgresql is used as the database. You can run the project using docker

**_Installation_**
1. Install `docker ` and ` docker-compose` on your machine


2. Run the container with the command
`docker-compose up`
   

3. Stop the container with the command
`docker-compose down`
   
**_Usage_**

***Creating a Django superuser***

`docker-compose run web python manage.py createsuperuser`

Create an .env file with the following logic:

`DB_ENGINE=django.db.backends.postgresql`

`DB_NAME=(name of your database)`

`POSTGRES_USER=(username for connection to database)`

`POSTGRES_PASSWORD=(set your own password)`

`DB_HOST=db (name of the tyoe if container)`

`DB_PORT=5432`

An example of initializing start data:

`docker-compose run web python manage.py loaddata fixtures.json`

To work with the API please refer to the documentation available in your browser at



