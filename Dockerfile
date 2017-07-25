FROM python

ADD ./requirements.txt /

RUN pip3 install -r requirements.txt

RUN mkdir -p app

VOLUME ['/app']

WORKDIR /app
