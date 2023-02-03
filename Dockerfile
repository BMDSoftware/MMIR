FROM python:3.8.10
LABEL author="Rodrigo Escobar Diaz Guerrero <redg@ua.pt>"

#RUN apt-get update && apt-get install
RUN apt-get update && \
    apt-get install ffmpeg libsm6 libxext6 libvips-dev -y && \
    apt-get clean
#RUN apt-get install ffmpeg libsm6 libxext6 libvips-dev -y
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install -r requirements.txt

WORKDIR /opt/app/

COPY ./  ./
CMD mv ./entrypoint.sh /ls

EXPOSE 5000

ENTRYPOINT ["/bin/bash", "/opt/app/entrypoint.sh"]
