import sqlite3

# Connect to DB
conn = sqlite3.connect('database.db')
c = conn.cursor()

# Insert dummy diseases
diseases = [
    ('Fever',),
    ('Diabetes',),
    ('Hypertension',),
    ('Asthma',),
    ('Allergy',),
    ('Cold and Cough',)
]

c.executemany('INSERT INTO disease (disease_name) VALUES (?)', diseases)

conn.commit()
conn.close()

print("Dummy diseases inserted successfully!")
