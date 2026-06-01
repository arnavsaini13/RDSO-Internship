#!/usr/bin/env python
import psycopg2
from psycopg2 import sql

# Connect to the default postgres database
conn = psycopg2.connect(
    host='127.0.0.1',
    port=5432,
    user='postgres',
    password='Arnav@132006',
    database='postgres'
)
conn.autocommit = True

# Create cursor
cur = conn.cursor()

try:
    # Check if database already exists
    cur.execute("SELECT 1 FROM pg_database WHERE datname = 'bdms_db'")
    if cur.fetchone() is None:
        cur.execute('CREATE DATABASE bdms_db OWNER arnavsaini13')
        print('✓ Database bdms_db created successfully')
    else:
        print('✓ Database bdms_db already exists')
finally:
    cur.close()
    conn.close()
