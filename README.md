# Planetarium-API project

DRF project for managing planetarium and watching shows

### How to run
```shell
git clone https://github.com/BornToLivee/planetarium-api
- copy .env.sample -> .env add fill it with all requirement data
- docker-compose up --build
- docker exec -it <container id> sh
- python managhe.py createsuperuser
```

## Features

* Managing planetarium shows, domes and themes
* Admin panel for advanced managing
* Cache system for several pages
* Documentation in api/doc/swagger/
* Message in telegram bot after creating new ticket
* Authentication and JWT authorization for user
* Creating, updating, deleting actions on all endpoints with validation

## Author

Bohdan Zinchenko - https://github.com/BornToLivee
