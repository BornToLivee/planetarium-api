# Planetarium-API project

DRF project for managing planetarium and watching shows

### How to run
```shell
git clone https://github.com/BornToLivee/planetarium-api
- copy .env.sample -> .env add fill it with all requirement data
- docker-compose up --build
- docker exec -it <container id> sh
- python managhe.py createsuperuser
- go to http://localhost:8000/api/planetarium/
```

## Features

* Managing planetarium shows, domes and themes
* Admin panel for advanced managing
* Cache system for several pages
* Documentation in api/doc/swagger/
* Message in telegram bot after creating new ticket
* Authentication and JWT authorization for user
* Creating, updating, deleting actions on all endpoints with validation

## Technology used

1.Django Rest Framework
2.Docker
3.PostgreSQL
4.Redis
5.Swagger
6.JWT


## Author

Bohdan Zinchenko - https://github.com/BornToLivee
