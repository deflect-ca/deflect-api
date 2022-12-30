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
RUN adduser deflect-core

# create the appropriate directories
ENV HOME=/home/deflect-core
ENV APP_HOME=/home/deflect-core/web
RUN mkdir $APP_HOME
RUN mkdir $APP_HOME/static
WORKDIR $APP_HOME

RUN apt-get update && apt-get install -y bind9utils netcat wait-for-it
COPY --from=builder /usr/src/deflect-core/wheels /wheels
COPY --from=builder /usr/src/deflect-core/requirements.txt .
RUN pip install --no-cache /wheels/*

# copy project
COPY . $APP_HOME

# Submodule
ENV PYTHONPATH "${PYTHONPATH}:/home/deflect-core/edgemanage3"
RUN cd edgemanage3 && python setup.py install

# chown all the files to the deflect-core user
RUN chown -R deflect-core:deflect-core $APP_HOME

# change to the app user
USER deflect-core
