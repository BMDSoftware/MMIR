FROM python:3.8.10
LABEL author="Rodrigo Escobar Diaz Guerrero <redg@ua.pt>"

WORKDIR /mmir_gui
COPY ./  ./


RUN apt-get update && apt-get install
RUN apt-get install ffmpeg libsm6 libxext6 libvips-dev -y
RUN python3 -m pip install --upgrade pip


RUN pip3 install -r requirements.txt

CMD [ "python", "manage.py","makemigrations", "--no-input"]
CMD [ "python", "manage.py","migrate", "--no-input"]
CMD [ "python", "create_admin.py"]



