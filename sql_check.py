#!/usr/bin/env python3

import os
import sys
from time import sleep
import MySQLdb as sql

env = os.environ

for n in range(10):
    try:
        sql.connect(host=env.get('DB_HOST'),
                    port=int(env.get('DB_PORT')),
                    user=env.get('DB_USER'),
                    password=env.get('DB_PASS'),
                    database=env.get('DB_NAME'))
    except sql.Error as e:
        print("Can't connect to SQL Server. Retrying in 30s")
        sleep(30)
    else:
        print("Connected to SQL Server successfully.")
        break
else:
    print("Could not connect to SQL Server over 5 Minutes. Please check the health of your SQL Server")
    sys.exit(1)