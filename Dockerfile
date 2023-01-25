FROM python:3.8.10
LABEL author="Rodrigo Escobar Diaz Guerrero <redg@ua.pt>"

WORKDIR /opt/app

COPY ./  ./
CMD mv ./entrypoint.sh /ls

RUN apt-get update && apt-get install
RUN apt-get install ffmpeg libsm6 libxext6 libvips-dev -y
RUN python3 -m pip install --upgrade pip

RUN pip3 install -r requirements.txt

EXPOSE 5000

ENTRYPOINT ["/bin/bash", "/opt/app/entrypoint.sh"]
