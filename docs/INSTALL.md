# Install

## System requirements

1. Python 3.6.10
2. Django 3.1
3. Django REST framework 3.11.1
4. MySQL 5.7 or above (JSON support)

## Deployment

```
git clone git@github.com:equalitie/deflect-core.git
git submodule update --init

# Init config and set SECRET_KEY
cp core/.env.example core/.env

# Docker start
docker compose up -d --build

# First time setup
docker compose exec web python manage.py migrate --noinput
docker compose exec web python manage.py collectstatic --no-input --clear
docker compose exec web python manage.py createsuperuser --email admin@example.com --username admin

# Docker stop
docker compose down

```

### Test in docker

Change the `web` section in `docker-compose` to:
```
command: >
  sh -c "edge_manage --config deploy/edgemanage/edgemanage.yaml --dnet dnet1 &&
         edge_query --config deploy/edgemanage/edgemanage.yaml --dnet dnet1 &&
         python manage.py test --noinput"
```

## Development

Deflect core could be installed in a python virtual env

    python -m venv venv
    source venv/bin/activate

Two git submodule, including `edgemanage` and `deflect-next` should be init and install

    git submodule update --init
    cd edgemanage3 && python setup.py install
    cd deflect_next/orchestration && pip install -r requirements.txt

After that, we could setup deflect-core, edit `.env` and setup database

    pip install -r requirements.txt
    cp core/.env.example core/.env
    python manage.py migrate
    python manage.py createsuperuser --email admin@example.com --username admin

Start the dev server with

    python manage.py runserver

### Celery (dev)

Run a celery worker with RabbitMQ for development

    python manage.py migrate django_celery_results  # first time
    rabbitmq-server
    celery -A core worker -l info

or change broker settings in `settings.py`

    CELERY_BROKER_URL = 'amqp://localhost'

### Edgemanage

After executing `python setup.py install` for edgemanage, there will be 3 binary installed

- edge_manage
- edge_query
- edge_conf

Directly executing these command should work as usual, but **an edgemanage config yaml is required** before running such command

1. `cp dev/edgemanage/edgemanage.example.yaml dev/edgemanage/edgemanage.yaml`
2. Edit `edgemanage.yaml`, replace `<abs_path>` with absolute path of this project directory (without trailing `/`)
3. Create `dev/edgemanage/edges/dev` and insert edges hostname, line by line

Execute commands to ensure edgemanage is installed correctly

    edge_manage --dnet dev --config dev/edgemanage/edgemanage.yaml -v
    edge_conf --dnet dev --config dev/edgemanage/edgemanage.yaml --mode unavailable --comment "out" {edge_hostname}
    edge_query --dnet dev --config dev/edgemanage/edgemanage.yaml -v
