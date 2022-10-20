FROM python:latest

WORKDIR /

ADD app /app
COPY poetry.lock pyproject.toml ./

RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry install
