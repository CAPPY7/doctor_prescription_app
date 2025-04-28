from flask import Flask, g, render_template, request, redirect, url_for, session, make_response,jsonify
import pdfkit
import sqlite3
import os

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps  # <-- added this

app = Flask(__name__)
app.secret_key = '24d1bb8ecf43f7c687dbd4fff2890925'
DATABASE = 'database.db'
# Use the environment variable for the port (Render automatically sets this)
port = int(os.environ.get("PORT", 5000))  # Default to 5000 if not set
app.run(host='0.0.0.0', port=port)  # '0.0.0.0' makes it accessible from any IP

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
    return g.db

@app.teardown_appcontext
def close_db(error):
    db = g.pop('db', None)
    if db is not None:
        db.close()

# --------- Added Login Required Decorator --------------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'doctor_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function
# --------------------------------------------------------

@app.route('/')
def home():
    if 'doctor_id' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('select_doctor'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        conn = get_db()
        c = conn.cursor()
        c.execute('SELECT * FROM doctor WHERE username = ?', (username,))
        doctor = c.fetchone()

        if doctor and check_password_hash(doctor[4], password):
            session['doctor_id'] = doctor[0]
            session['doctor_name'] = doctor[1]
            return redirect(url_for('select_doctor'))
        else:
            error = "Invalid Username or Password!"
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/select_doctor', methods=['GET', 'POST'])
@login_required
def select_doctor():
    conn = get_db()
    c = conn.cursor()
    if request.method == 'POST':
        doctor_id = request.form.get('doctor')
        return redirect(url_for('select_disease', doctor_id=doctor_id))

    c.execute('SELECT * FROM doctor')
    doctors = c.fetchall()
    return render_template('select_doctor.html', doctors=doctors)

@app.route('/select_disease/<int:doctor_id>', methods=['GET', 'POST'])
@login_required
def select_disease(doctor_id):
    conn = get_db()
    c = conn.cursor()
    if request.method == 'POST':
        disease_id = request.form.get('disease')
        return redirect(url_for('select_medicine', disease_id=disease_id, doctor_id=doctor_id))

    c.execute('SELECT * FROM disease')
    diseases = c.fetchall()
    return render_template('select_disease.html', diseases=diseases, doctor_id=doctor_id)

@app.route('/select_medicine/<int:disease_id>/<int:doctor_id>', methods=['GET', 'POST'])
@login_required
def select_medicine(disease_id, doctor_id):
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT disease_name FROM disease WHERE id = ?', (disease_id,))
    disease_name = c.fetchone()[0]
    c.execute('SELECT medicine_name FROM medicine')
    medicines = c.fetchall()

    if request.method == 'POST':
        selected_meds = request.form.getlist('medicines')

        new_medicine = request.form.get('name')
        new_dosage = request.form.get('dosage')
        if new_medicine and new_dosage:
            c.execute('INSERT INTO medicine (medicine_name, dosage, disease_related) VALUES (?, ?, ?)',
                      (new_medicine, new_dosage, disease_name))
            conn.commit()
            selected_meds.append(new_medicine)

        medicines_str = ', '.join(selected_meds)
        return redirect(url_for('enter_vitals', disease_id=disease_id, doctor_id=doctor_id, medicines=medicines_str))

    return render_template('select_medicine.html', disease_name=disease_name, medicines=medicines, disease_id=disease_id, doctor_id=doctor_id)

@app.route('/enter_vitals', methods=['GET', 'POST'])
@login_required
def enter_vitals():
    medicines = request.args.get('medicines', '')
    doctor_id = request.args.get('doctor_id')
    disease_id = request.args.get('disease_id')

    if request.method == 'POST':
        heart_rate = request.form.get('heart_rate')
        blood_pressure = request.form.get('blood_pressure')
        blood_sugar = request.form.get('blood_sugar')
        hemoglobin = request.form.get('hemoglobin')
        temperature = request.form.get('temperature')
        respiratory_rate = request.form.get('respiratory_rate')
        weight = request.form.get('weight')
        height = request.form.get('height')
        patient_name = request.form.get('patient_name')
        patient_age = request.form.get('patient_age')

        if not heart_rate or not blood_pressure or not patient_name or not patient_age:
            return "Please fill in all required fields!", 400

        return redirect(url_for('final_prescription',
                                heart_rate=heart_rate,
                                blood_pressure=blood_pressure,
                                blood_sugar=blood_sugar,
                                hemoglobin=hemoglobin,
                                temperature=temperature,
                                respiratory_rate=respiratory_rate,
                                weight=weight,
                                height=height,
                                medicines=medicines,
                                doctor_id=doctor_id,
                                disease_id=disease_id,
                                patient_name=patient_name,
                                patient_age=patient_age))

    return render_template('enter_vitals.html', medicines=medicines, doctor_id=doctor_id, disease_id=disease_id)

@app.route('/final_prescription', methods=['GET', 'POST'])
@login_required
def final_prescription():
    if request.method == 'POST':
        conn = get_db()
        c = conn.cursor()
        heart_rate = request.form.get('heart_rate')
        blood_pressure = request.form.get('blood_pressure')
        blood_sugar = request.form.get('blood_sugar')
        hemoglobin = request.form.get('hemoglobin')
        medicines = request.form.get('medicines')
        doctor_id = request.form.get('doctor_id')
        disease_id = request.form.get('disease_id')

        now = datetime.now()
        date_str = now.strftime("%d-%m-%Y")
        time_str = now.strftime("%H:%M:%S")

        try:
            c.execute('''INSERT INTO prescription 
                         (doctor_id, disease_id, medicines, heart_rate, blood_pressure, blood_sugar, hemoglobin, date, time)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                         (doctor_id, disease_id, medicines, heart_rate, blood_pressure, blood_sugar, hemoglobin, date_str, time_str))
            conn.commit()
        except sqlite3.Error as e:
            print(f"Error inserting prescription: {e}")
            return "Error saving prescription, please try again later.", 500

        return "Prescription Saved Successfully!"

    else:
        heart_rate = request.args.get('heart_rate')
        blood_pressure = request.args.get('blood_pressure')
        blood_sugar = request.args.get('blood_sugar')
        hemoglobin = request.args.get('hemoglobin')
        temperature = request.args.get('temperature')
        respiratory_rate = request.args.get('respiratory_rate')
        weight = request.args.get('weight')
        height = request.args.get('height')
        medicines = request.args.get('medicines')
        doctor_id = request.args.get('doctor_id')
        disease_id = request.args.get('disease_id')
        patient_name = request.args.get('patient_name')
        patient_age = request.args.get('patient_age')
        doctor_name = session.get('doctor_name', 'Unknown Doctor')
        clinic_name = "City Health Clinic"

        now = datetime.now()
        date_str = now.strftime("%d-%m-%Y")
        time_str = now.strftime("%H:%M:%S")

        return render_template('final_prescription.html',
                               heart_rate=heart_rate,
                               blood_pressure=blood_pressure,
                               blood_sugar=blood_sugar,
                               hemoglobin=hemoglobin,
                               temperature=temperature,
                               respiratory_rate=respiratory_rate,
                               weight=weight,
                               height=height,
                               medicines=medicines.split(','),
                               date=date_str,
                               time=time_str,
                               doctor_id=doctor_id,
                               disease_id=disease_id,
                               medicines_str=medicines,
                               patient_name=patient_name,
                               patient_age=patient_age,
                               doctor_name=doctor_name,
                               clinic_name=clinic_name)

@app.route('/download_prescription')
@login_required
def download_prescription():
    doctor_id = request.args.get('doctor_id')
    disease_id = request.args.get('disease_id')
    medicines = request.args.get('medicines').split(',')
    heart_rate = request.args.get('heart_rate')
    blood_pressure = request.args.get('blood_pressure')
    blood_sugar = request.args.get('blood_sugar')
    hemoglobin = request.args.get('hemoglobin')
    temperature = request.args.get('temperature')
    respiratory_rate = request.args.get('respiratory_rate')
    weight = request.args.get('weight')
    height = request.args.get('height')
    patient_name = request.args.get('patient_name')
    patient_age = request.args.get('patient_age')
    doctor_name = session.get('doctor_name', 'Unknown Doctor')
    clinic_name = "City Health Clinic"

    now = datetime.now()
    date_str = now.strftime("%d-%m-%Y")
    time_str = now.strftime("%H:%M:%S")

    rendered = render_template('prescription_pdf.html',
                                doctor_id=doctor_id,
                                disease_id=disease_id,
                                medicines=medicines,
                                heart_rate=heart_rate,
                                blood_pressure=blood_pressure,
                                blood_sugar=blood_sugar,
                                hemoglobin=hemoglobin,
                                temperature=temperature,
                                respiratory_rate=respiratory_rate,
                                weight=weight,
                                height=height,
                                date=date_str,
                                time=time_str,
                                patient_name=patient_name,
                                patient_age=patient_age,
                                doctor_name=doctor_name,
                                clinic_name=clinic_name)

    pdf = pdfkit.from_string(rendered, False)
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=prescription.pdf'
    return response

# ------------------- API Route to Send JSON -------------------
@app.route('/api/prescriptions', methods=['GET'])
def get_prescriptions():
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT id, doctor_id, disease_id, medicines, heart_rate, blood_pressure, blood_sugar, hemoglobin, date, time FROM prescription')
    prescriptions = c.fetchall()

    result = []
    for p in prescriptions:
        result.append({
            "id": p[0],
            "doctor_id": p[1],
            "disease_id": p[2],
            "medicines": p[3],
            "heart_rate": p[4],
            "blood_pressure": p[5],
            "blood_sugar": p[6],
            "hemoglobin": p[7],
            "date": p[8],
            "time": p[9]
        })

    return jsonify(result)
# ---------------------------------------------------------------



if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # default to 5000 if no PORT env variable
    app.run(host="0.0.0.0", port=port, debug=True)