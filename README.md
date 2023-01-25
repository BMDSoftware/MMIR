# MMIR GUI

MMIR GUI is a web interface that allows the user:


- Execution of a pipeline for image registration using different algorithms.

- Visualize the annotations as semantic segmentation.

- Visualize the images with a pyramid organization.

### Brief overview
MMIR-Gui is a web-based system that allows the end-user to register biological images and compare the outcomes of different algorithms through visualization tools. 
Our system contains three main modules: (1) a system manager, (2) an algorithm manager, and (3) an image visualization system (Fig. 1). 
The system manager creates, reads, updates, and deletes projects, as well as establish a direct connection with the database where the initial images and results will be stored. 
The algorithm manager oversees carrying out the execution pipeline of each algorithm using a plugin architecture. Finally, the visualization system allows to the user interact with the results through different visualization tools. 
The system was developed using the framework Django, JavaScript, and multiple libraries that facilitate the management and annotation of very high-resolution images.

![img_2.png](img_2.png)
Figure 1: Proposed registration system with three main modules. A system manager, An algorithm manager, and an image visualization system.

### Initialize without docker
Dependencies:
- MySQL
- Python 3

Go to the branch "LocalDeploy" and download all the files. 
Configure the database connections with the file mmmir_gui/settings.py 
```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'mmirdb',
        'USER': 'redg',
        'PASSWORD': 'mmir2022',
        'HOST': '127.0.0.1',
        'PORT': '3306',
        'CONN_MAX_AGE': 600,
        'OPTIONS': {
            'sql_mode' : 'STRICT_TRANS_TABLES',
            'autocommit': True,

        }
    }
}

```
Then Install all the requirement libraries:
```
pip install -r requirements.txt
```
Generate the migrations
```
python manage.py makemigrations
```
Migrate to mysql
```
python manage.py migrate
```
Run the server
```
Python manage.py runserver
```
### Initialize with docker
Dependencies:
- Docker
- Docker-compose

Go to the branch "LocalDeploy" and download all the files. 
Build the image
```
docker-compose build
```
Run the MySQL container
```
docker-compose up db
```
Run the server

```
docker-compose up -d
```
### Batch vs Single Registration
With MMIR-Gui you can perform the registration of a pair of images or a batch of pairs.
The batch system allows you to load n number of files and n number of annotations. By choosing this option you should load the same number of files in the fixing images, moving images, and annotations, except if a JSON file is used.

### Inputs
Internally all images are read using the python OpenCV library, so only the formats of this library are supported, in the future we intend to add more extensions related to biological formats.

#### Annotations
There are 3 ways to load annotations, through images, using .npz files or through JSON files using the COCO format.

#### COCO format

### Plugins

