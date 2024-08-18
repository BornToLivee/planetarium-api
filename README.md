# Planetarium-API project

DRF project for managing planetarium and watching shows

### How to run

1. Clone the Repository
```shell
git clone https://github.com/BornToLivee/planetarium-api
```
If project is empty, checkout to develop branch

2. Configure Environment Variables
```shell
cp .env.sample .env
```
Open the .env file and fill in all the required fields with the appropriate data.
3. Build and Run the Docker Containers
```shell
docker-compose up --build
```
4. Create a Superuser

List the running Docker containers to find the container_id of the web service:
```shell
docker ps
```
Access the running container with:
```shell
docker exec -it <container_id> sh
```
Inside the container, create a superuser by running:
```shell
python manage.py createsuperuser
```
5. Access the API
http://localhost:8000/api/planetarium/

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
