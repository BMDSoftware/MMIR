# MMIR_GUI

A web interface that allows the user:

• Visualize multimodal and H&E images.

• Visualize the GT as semantic segmentation.

• Creation of triggers that initiate the pipeline of the coregistration process using artificial intelligence techniques.

### Brief overview
The system uses the "Django" framework as backend, and different technologies in the front-end. Mainly Java Script.

All projects are stored in a MySQL database. 

Algorithms can be added or modified in main/views.py. In particular in the runAlg() function. Also the name of the algorithms must be present in the Algorithms table of the database.
