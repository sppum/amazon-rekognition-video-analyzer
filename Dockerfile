FROM debian:latest
WORKDIR /srv
ENV PYTHONPATH $PYTHONPATH:/usr/lib/python2.7/site-packages/botocore_amazon
RUN apt-get update \
    && apt-get install -y python2.7 python-pip \
        python-opencv git vim \
    && pip install pipenv \
    && cd /srv \
#    && pipenv --two \
#    && pipenv shell \
    && pip install numpy boto3 pynt awscli pytz requests urllib3

#COPY *.* /srv/

# If not mounting a directory with a copy of the repo...
# && git clone $GIT_URL
# && pip install pytz -t /path/to/repo/lambda/imageprocessor/
