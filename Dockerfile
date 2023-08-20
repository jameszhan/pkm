FROM python:3.9-bullseye

WORKDIR /app
RUN mkdir -p /app/pip_cache
RUN mkdir -p /app/pkm

RUN set -xe;

RUN apt-get update && apt-get install tini -y --no-install-recommends

COPY requirements/production.txt /app/requirements.txt
RUN python -m pip install --upgrade pip --cache-dir /app/pip_cache; \
    pip install -r requirements.txt --cache-dir /app/pip_cache

COPY . /app/pkm

RUN useradd -m -s /bin/bash -u 1026 deploy; \
    chown -R deploy:deploy /app

USER deploy
EXPOSE 8000/tcp
ENTRYPOINT [ "tini", "--" ]
CMD [ "python3", "/app/pkm/manage.py", "runserver", "0.0.0.0:8000" ]