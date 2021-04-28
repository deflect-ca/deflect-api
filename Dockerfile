###########
# BUILDER #
###########

FROM python:3.6-buster as builder
WORKDIR /usr/src/deflect-core

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN apt-get update && apt-get install -y libmariadb-dev bind9utils
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/deflect-core/wheels -r requirements.txt


#########
# FINAL #
#########

FROM python:3.6-buster

# create directory for the deflect-core user
RUN mkdir -p /home/deflect-core

# create the deflect-core user
RUN addgroup -S deflect-core && adduser -S deflect-core -G deflect-core

# create the appropriate directories
ENV HOME=/home/deflect-core
ENV APP_HOME=/home/deflect-core/web
RUN mkdir $APP_HOME
WORKDIR $APP_HOME

RUN apt-get update && apt-get install -y bind9utils netcat
COPY --from=builder /usr/src/deflect-core/wheels /wheels
COPY --from=builder /usr/src/deflect-core/requirements.txt .
RUN pip install --no-cache /wheels/*
COPY ./edgemanage3 edgemanage3
RUN cd edgemanage3 && python setup.py install

COPY ./entrypoint.prod.sh $APP_HOME

# copy project
COPY . $APP_HOME

# chown all the files to the deflect-core user
RUN chown -R deflect-core:deflect-core $APP_HOME

# change to the app user
USER deflect-core

ENTRYPOINT ["/usr/src/deflect-core/entrypoint.sh"]
