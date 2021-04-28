FROM python:3.6-buster

# set work directory
WORKDIR /usr/src/deflect-core

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN apt-get update && apt-get install -y libmariadb-dev bind9utils netcat
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt
COPY ./edgemanage3 edgemanage3
RUN cd edgemanage3 && python setup.py install

# copy project
COPY . .

ENTRYPOINT ["/usr/src/deflect-core/entrypoint.sh"]
