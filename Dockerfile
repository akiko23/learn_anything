FROM python:3.12-alpine

WORKDIR code

COPY . .

RUN chmod -R 777 scripts && sh -c "$(cat scripts/init_playground_host.sh)"

RUN pip3 install --upgrade  poetry==1.8.3

RUN python3 -m poetry config virtualenvs.create false \
    && python3 -m poetry install --no-interaction --no-ansi --without dev \
    && echo yes | python3 -m poetry cache clear . --all
