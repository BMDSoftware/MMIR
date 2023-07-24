FROM python:3.8.10
LABEL author="Rodrigo Escobar Diaz Guerrero <redg@ua.pt>"

RUN apt-get update && \
    apt-get install ffmpeg libsm6 libxext6 libvips-dev nginx -y --no-install-recommends && \
    apt-get clean
RUN python3 -m pip install --upgrade pip

COPY ./requirements.txt ./requirements.txt
RUN python3 -m pip install -r requirements.txt

RUN rm /etc/nginx/sites-enabled/*
COPY ./nginx/nginx.conf /etc/nginx/sites-enabled/mmir-gui.conf

ENV APP_HOME=/opt/app
RUN mkdir $APP_HOME
RUN mkdir $APP_HOME/staticfiles
RUN mkdir $APP_HOME/media
RUN mkdir /tmp/client_body_temp
WORKDIR $APP_HOME

COPY ./  ./
CMD mv ./entrypoint.sh /ls



EXPOSE 5000

ENTRYPOINT ["/bin/bash", "/opt/app/entrypoint.sh"]
