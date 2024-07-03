FROM python:3.12

WORKDIR /code

RUN pip install poetry

COPY poetry.lock pyproject.toml /code/

RUN poetry config virtualenvs.create false && poetry install --no-dev

COPY ./app /code/app

WORKDIR /code/app

CMD ["poetry", "run", "uvicorn", "main:app", "--port", "8000"]
