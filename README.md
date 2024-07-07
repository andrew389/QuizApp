# Quizz App

## Table of Contents

- [Installation](#installation)
- [Running without Docker](#running-without-docker)
    - [Running Tests](#running-tests)
    - [Running Migrations](#running-migrations)
- [Running in Docker](#running-in-docker)
    - [Running Tests](#running-tests-1)
    - [Running Migrations](#running-migrations-1)
    - [Stopping Docker and cleaning](#stopping-docker-and-cleaning)

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/andrew389/meduzzen_internship.git
    cd meduzzen_internship
    ```

2. Install poetry:

    ```bash
    pip install poetry
    ```

3. Install the dependencies:

    ```bash
    poetry install
    ```

4. Create and activate a virtual environment:

    ```bash
    poetry shell
    ```

5. Run the FastAPI application using Uvicorn:

    ```bash
    uvicorn main:app --reload
    ```

6. Open your browser and go to http://127.0.0.1:8000 to see the application running.

### Running Tests

1. Open `.env` file and change `REDIS_DB_HOST` and `POSTGRES_DB_HOST`:

    ```bash
    REDIS_DB_HOST=localhost
    POSTGRES_DB_HOST=localhost
    ```

2. Make sure this line in `app/tests/test_redis.py` looks like this:

    ```bash
    with patch.object(settings.redis, 'host', 'localhost')
    ```

3. Open a console and run pytest:

    ```bash
    pytest -v
    ```

### Running Migrations

1. Make sure these lines in `app/alembic.ini` look like this:

    ```bash
    sqlalchemy.url = postgresql://postgres:postgres@localhost/main
    ```

2. Open a bash console:

    ```bash
    alembic revision --autogenerate -m "first commit"
    ```

3. Update the database to the latest migration:

    ```bash
    alembic upgrade head
    ```

## Running in Docker

Before you begin, make sure you have the following programs installed on your computer:

- Docker: [Docker Installation Guide](https://docs.docker.com/get-docker/)
- Docker Compose: [Docker Compose Installation Guide](https://docs.docker.com/compose/install/)

### Steps

1. Start containers using Docker Compose:

    ```bash
    docker-compose up -d --build
    ```

   _The `-d` option runs containers in the background._

2. After successful launch, access your project at http://localhost:8010 in your web browser.

### Running Tests

1. Open `.env` file and change `REDIS_DB_HOST` and `POSTGRES_DB_HOST`:

    ```bash
    REDIS_DB_HOST=redis
    POSTGRES_DB_HOST=test_db
    ```

2. Make sure this line in `app/tests/test_redis.py` looks like this:

    ```bash
    with patch.object(settings.redis, 'host', 'redis')
    ```

3. To run tests inside the Docker container:

   - Stop your docker-compose if it's running and start docker-compose for tests:

    ```bash
    docker-compose -f docker-compose.yml down
    docker-compose -f docker-compose.test.yml up -d --build
    ```

   - Then, identify the container ID by listing all running containers:

    ```bash
    docker ps
    ```

   - Note down the CONTAINER ID of your app container.

   - Open a bash shell inside the container using its ID:

    ```bash
    docker exec -it [CONTAINER ID] bash
    ```

   - Inside the container's bash shell, run pytest to execute tests:

    ```bash
    pytest -v
    ```

   - You should see output indicating that the tests have passed.

   - Leave the bash console:

    ```bash
    exit
    ```

   - Stop docker-compose:

    ```bash
    docker-compose -f docker-compose.test.yml down
    ```

### Running Migrations

1. Make sure these lines in `app/alembic.ini` look like this:

    ```bash
    sqlalchemy.url = postgresql://postgres:postgres@main_db/main
    ```

2. Open a bash shell inside the container:

    ```bash
    cd app
    alembic revision --autogenerate -m "init"
    ```

3. Update the database to the latest migration:

    ```bash
    alembic upgrade head
    ```

4. Leave the bash console:

    ```bash
    exit
    ```

5. Continue using the application.

### Stopping Docker and cleaning

1. Stop your main docker-compose:

    ```bash
    docker-compose -f docker-compose.yml down
    ```

2. Clean all containers and images:

    ```bash
    docker rm $(docker ps -a -q)
    docker rmi $(docker images -q)
    ```
