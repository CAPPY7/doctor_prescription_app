import sqlite3

# Connect to DB
conn = sqlite3.connect('database.db')
c = conn.cursor()

# Insert dummy doctors
doctors = [
    ('Dr. Amit Sharma', 'Cardiologist'),
    ('Dr. Priya Kapoor', 'Neurologist'),
    ('Dr. Rahul Verma', 'General Physician'),
    ('Dr. Neha Gupta', 'Dermatologist')
]

c.executemany('INSERT INTO doctor (name, specialization) VALUES (?, ?)', doctors)

conn.commit()
conn.close()

print("Dummy doctors inserted successfully!")
