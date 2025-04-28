import sqlite3

# Connect to DB
conn = sqlite3.connect('database.db')
c = conn.cursor()

# Insert dummy medicines
medicines = [
    ('Paracetamol', 'Fever'),
    ('Ibuprofen', 'Fever'),
    ('Metformin', 'Diabetes'),
    ('Losartan', 'Hypertension'),
    ('Salbutamol', 'Asthma'),
    ('Cetirizine', 'Allergy'),
    ('Cough Syrup', 'Cold and Cough')
]

c.executemany('INSERT INTO medicine (medicine_name, disease_related) VALUES (?, ?)', medicines)

conn.commit()
conn.close()

print("Dummy medicines inserted successfully!")
