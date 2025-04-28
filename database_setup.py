import sqlite3
from werkzeug.security import generate_password_hash

# Connect to database
conn = sqlite3.connect('database.db')
c = conn.cursor()

# Drop existing tables
c.execute('DROP TABLE IF EXISTS doctor')
c.execute('DROP TABLE IF EXISTS disease')
c.execute('DROP TABLE IF EXISTS medicine')
c.execute('DROP TABLE IF EXISTS prescription')

# Create tables
c.execute('''
    CREATE TABLE doctor (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        specialization TEXT NOT NULL,
        username TEXT NOT NULL,
        password TEXT NOT NULL
    )
''')

c.execute('''
    CREATE TABLE disease (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        disease_name TEXT NOT NULL,
        description TEXT NOT NULL,
        diet_recommendations TEXT,
        foods_to_avoid TEXT,
        exercise_advice TEXT,
        lifestyle_tips TEXT,
        important_warnings TEXT
    )
''')

c.execute('''
    CREATE TABLE medicine (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        medicine_name TEXT NOT NULL,
        disease_related TEXT,
        dosage TEXT
    )
''')

c.execute('''
    CREATE TABLE prescription (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        doctor_id INTEGER,
        disease_id INTEGER,
        medicines TEXT,
        heart_rate TEXT,
        blood_pressure TEXT,
        blood_sugar TEXT,
        hemoglobin TEXT,
        date TEXT,
        time TEXT,
        FOREIGN KEY (doctor_id) REFERENCES doctor(id),
        FOREIGN KEY (disease_id) REFERENCES disease(id)
    )
''')

# Insert sample doctor with hashed password
hashed_password = generate_password_hash("password123")
c.execute('''
    INSERT INTO doctor (name, specialization, username, password)
    VALUES (?, ?, ?, ?)
''', ("Dr. Rahul Mehta", "General Physician", "rahul", hashed_password))

# Insert sample diseases
c.executemany('''
    INSERT INTO disease (disease_name, description, diet_recommendations, foods_to_avoid, exercise_advice, lifestyle_tips, important_warnings)
    VALUES (?, ?, ?, ?, ?, ?, ?)
''', [
    ("Cardiovascular Diseases", "Heart and blood vessel disorders.", "Low-salt diet, high-fiber foods", "Avoid fried foods, excess salt", "30 minutes brisk walking", "Quit smoking, control cholesterol", "Chest pain? Seek emergency care."),
    ("Diabetes Mellitus (Type 2)", "Chronic blood sugar disorder.", "Complex carbs, avoid sugary foods", "Sweets, soft drinks", "Daily walk, yoga", "Lose weight, control sugar", "Foot care very important."),
    ("Hypertension", "High blood pressure condition.", "Low-sodium diet", "Pickles, processed foods", "Morning walk, meditation", "Stress management", "High BP can cause stroke."),
    ("Anemia", "Low red blood cell count.", "Iron-rich foods like spinach", "Avoid tea/coffee after meals", "Light exercise", "Increase iron intake", "Severe anemia needs transfusion."),
    ("Tuberculosis (TB)", "Lung infection by bacteria.", "High-protein diet", "Alcohol, smoking", "Deep breathing exercises", "Finish full course of medicine", "Skipping medicine worsens TB."),
])

# Insert sample medicines (ONLY with dosage)
c.executemany('''
    INSERT INTO medicine (medicine_name, disease_related, dosage)
    VALUES (?, ?, ?)
''', [
    ("Aspirin (Ecospirin)", "Cardiovascular Diseases", "75 mg once daily after food"),
    ("Metformin (Glucophage)", "Diabetes Mellitus (Type 2)", "500 mg twice daily after meals"),
    ("Amlodipine (Norvasc)", "Hypertension", "5 mg once daily"),
    ("Ferrous Sulfate (Feosol)", "Anemia", "325 mg once or twice daily"),
    ("Isoniazid", "Tuberculosis (TB)", "300 mg once daily"),
])

# Save and close
conn.commit()
conn.close()

print("✅ Database and tables created successfully with updated structure and sample data!")
