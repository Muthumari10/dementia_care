from flask import Flask, render_template, request, redirect, session, url_for, flash, jsonify, Response
import mysql.connector
import hashlib
from datetime import datetime
from flask_mail import Mail, Message
from apscheduler.schedulers.background import BackgroundScheduler
import pandas as pd
import joblib
from sklearn.preprocessing import LabelEncoder
import pyttsx3
import datetime
from datetime import date
from datetime import datetime
import time
import pandas as pd
from difflib import get_close_matches
import os
import requests
import cv2
import numpy as np
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense
from tensorflow.keras.preprocessing.image import img_to_array, load_img
from werkzeug.utils import secure_filename
from keras.models import load_model
from flask import request, jsonify, session
from PIL import Image
from urllib.parse import quote_plus
import threading

app = Flask(__name__)
app.secret_key = 'secret123'

# -------------------------------
# Database Connection
# -------------------------------
def get_db_connection():
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='dementia_care',
        charset='utf8',
        buffered=True 
    )
    return conn

# -------------------------------
# Flask Mail Config
# -------------------------------
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'cakilesh65@gmail.com'
app.config['MAIL_PASSWORD'] = 'ompn xqih vfoo pnct'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
mail = Mail(app)

# -------------------------------
# Load Dementia Model
# -------------------------------
model = joblib.load('dementia_model.pkl')
encoders = joblib.load('dementia_encoders.pkl')

# -------------------------------
# Home Route
# -------------------------------
@app.route('/')
def home():
    return render_template('index.html')

# -------------------------------
# Patient Routes
# -------------------------------
@app.route('/patient/register', methods=['GET','POST'])
def patient_register():
    if request.method == 'POST':
        name = request.form['name']
        mobile = request.form['mobile']
        email = request.form['email']
        location = request.form['location']
        username = request.form['username']
        password = hashlib.sha256(request.form['password'].encode()).hexdigest()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO patients (name, mobile, email, location, username, password) VALUES (%s,%s,%s,%s,%s,%s)",
                       (name,mobile,email,location,username,password))
        conn.commit()
        cursor.close()
        conn.close()
        flash("Patient Registered Successfully")
        return redirect(url_for('patient_login'))
    return render_template('patient_register.html')

@app.route('/patient/login', methods=['GET','POST'])
def patient_login():
    if request.method == 'POST':
        username = request.form['username']
        password = hashlib.sha256(request.form['password'].encode()).hexdigest()

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Check credentials
        cursor.execute(
            "SELECT * FROM patients WHERE username=%s AND password=%s",
            (username, password)
        )
        user = cursor.fetchone()

        # Get client IP
        ip_address = request.remote_addr

        # Determine login status
        status = 'success' if user else 'failed'

        # Insert login activity
        cursor.execute(
            "INSERT INTO login_activity (user_id, role, login_time, ip_address, status) "
            "VALUES (%s, 'patient', NOW(), %s, %s)",
            (user['id'] if user else 0, ip_address, status)
        )
        conn.commit()
        cursor.close()
        conn.close()

        if user:
            session['patient_id'] = user['id']
            session['patient_name'] = user['name']
            session['patient_mobile'] = user['mobile']
            return redirect(url_for('patient_dashboard'))  # Redirect to patient dashboard/profile
        else:
            flash("Invalid Credentials")

    return render_template('patient_login.html')

@app.route('/patient/dashboard')
def patient_dashboard():
    st=""
    if 'patient_id' not in session:
        return redirect(url_for('patient_login'))

    patient_id = session['patient_id']
    patient_name = session['patient_name']
    patient_mobile = session['patient_mobile']

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Fetch all upcoming reminders
    cursor.execute("""
        SELECT id, title, description, datetime, sms_sent
        FROM reminders
        WHERE patient_id = %s
    """, (patient_id,))
    reminders = cursor.fetchall()


        
    cursor.close()
    conn.close()

    

    return render_template('patient_dashboard.html', patient_id=patient_id,
                           patient_name=patient_name,
                           patient_mobile=patient_mobile,
                           reminders=reminders)

@app.route('/page')
def page():
    st = ""
    mess = ""

    if 'patient_id' not in session:
        return redirect(url_for('patient_login'))

    patient_id = session['patient_id']
    patient_name = session['patient_name']
    patient_mobile = session['patient_mobile']

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Fetch reminders for this patient
    cursor.execute("""
        SELECT id, title, description, datetime, sms_sent
        FROM reminders
        WHERE patient_id = %s
    """, (patient_id,))
    reminders = cursor.fetchall()

    # Current time
    now = datetime.now()
    current_date = now.date()
    current_hour = now.hour
    current_minute = now.minute

    for d1 in reminders:
        reminder_dt = d1['datetime']      # datetime object
        sms_sent = d1['sms_sent']
        title = d1['title']
        description = d1['description']

        reminder_date = reminder_dt.date()
        reminder_hour = reminder_dt.hour
        reminder_minute = reminder_dt.minute

        # Check if reminder time has passed
        if (
            reminder_date == current_date and
            reminder_hour == current_hour and
            current_minute >= reminder_minute and
            sms_sent == 0
        ):
            st = "1"
            mess = f"{title}, {description}"

            cursor.execute("""
                UPDATE reminders
                SET sms_sent = 1
                WHERE id = %s
            """, (d1['id'],))

            conn.commit()

    cursor.close()
    conn.close()

    return render_template(
        'page.html',
        patient_id=patient_id,
        patient_name=patient_name,
        patient_mobile=patient_mobile,
        reminders=reminders,
        st=st,
        mess=mess
    )

# -------------------------------
# Dementia Test Route
# -------------------------------
@app.route('/patient/dementia_test', methods=['GET','POST'])
def dementia_test():
    if 'patient_id' not in session:
        return redirect(url_for('patient_login'))
    
    result = None
    if request.method == 'POST':
        # Collect inputs
        data = {
            'age': int(request.form['age']),
            'gender': request.form['gender'],
            'blood_pressure': request.form['blood_pressure'],
            'cholesterol': int(request.form['cholesterol']),
            'stress_level': request.form['stress_level'],
            'depression_level': request.form['depression_level'],
            'alcohol_consumption': request.form['alcohol_consumption'],
            'smoking_habit': request.form['smoking_habit'],
            'academic_performance': request.form['academic_performance'],
            'sleep_quality': request.form['sleep_quality'],
            'internet_addiction': request.form['internet_addiction'],
            'physical_activity': request.form['physical_activity']
        }

        # Convert to DataFrame
        input_df = pd.DataFrame([data])

        # -----------------------------
        # Encode categorical columns safely
        # -----------------------------
        cat_cols = ['gender','blood_pressure','stress_level','depression_level',
                    'alcohol_consumption','smoking_habit','academic_performance',
                    'sleep_quality','internet_addiction','physical_activity']

        # Load saved encoders
        encoders = joblib.load('dementia_encoders.pkl')  # you should save them when training

        for col in cat_cols:
            if col in input_df.columns:
                le = encoders[col]
                # Replace unseen labels with first known class
                input_df[col] = input_df[col].apply(lambda x: x if x in le.classes_ else le.classes_[0])
                input_df[col] = le.transform(input_df[col])

        # Predict using model
        prediction = model.predict(input_df)[0]
        result = 'Yes' if prediction==1 else 'No'

        # -----------------------------
        # Store result in database
        # -----------------------------
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO dementia_tests
            (patient_id, age, blood_pressure, cholesterol, memory_test_1, memory_test_2,
            attention_test, language_test, orientation_test, problem_solving_test,
            daily_activity_score, visual_spatial_score, social_interaction_score, result)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, [session['patient_id'], data['age'], data['blood_pressure'], data['cholesterol'],
              0,0,0,0,0,0,0,0,0,result])
        conn.commit()
        cursor.close()
        conn.close()

        flash(f"Dementia Prediction Result: {result}")

    return render_template('dementia_test.html', result=result)

# -------------------------------
# Add Reminder
# -------------------------------
@app.route('/patient/add_reminder', methods=['GET','POST'])
def add_reminder():
    if 'patient_id' not in session:
        return redirect(url_for('patient_login'))

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        datetime_str = request.form['datetime']
        dt = datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M')

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO reminders (patient_id, title, description, datetime, sms_sent)
            VALUES (%s, %s, %s, %s, 0)
        """, (session['patient_id'], title, description, dt))
        conn.commit()
        cursor.close()
        conn.close()

        flash("Reminder Added Successfully!")

    return render_template('add_reminder.html')

# -------------------------------
# Email Reminder Function
# -------------------------------
def send_reminder_email(reminder):
    with app.app_context():  # Ensure Flask context for background job
        # HTML email content
        html_content = f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #f9f9f9;
                    padding: 20px;
                }}
                .container {{
                    background-color: #ffffff;
                    padding: 20px;
                    border-radius: 10px;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                    max-width: 600px;
                    margin: auto;
                }}
                h2 {{
                    color: #4CAF50;
                }}
                p {{
                    font-size: 16px;
                    line-height: 1.5;
                    color: #333333;
                }}
                .footer {{
                    margin-top: 20px;
                    font-size: 14px;
                    color: #777777;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2>Hello {reminder['name']},</h2>
                <p><strong>Reminder:</strong> {reminder['title']}</p>
                <p><strong>Details:</strong> {reminder['description']}</p>
                <p><strong>Scheduled Time:</strong> {reminder['datetime']}</p>
                <p>Please take the necessary action.</p>
                <div class="footer">
                    This is an automated reminder from your Dementia Care Companion system.
                </div>
            </div>
        </body>
        </html>
        """

        # Create email message
        msg = Message(
            subject=f"Reminder: {reminder['title']}",
            sender=app.config['MAIL_USERNAME'],
            recipients=[reminder['email']],
            html=html_content  # use HTML instead of plain text
        )

        mail.send(msg)
        print(f"Email sent to {reminder['email']} for reminder: {reminder['title']}")
# -------------------------------
# SMS Reminder Function
# -------------------------------
@app.route('/patient/mark_sms_sent/<int:reminder_id>', methods=['POST'])
def mark_sms_sent(reminder_id):
    try:
        conn = get_db_connection()  # your DB connection function
        cursor = conn.cursor()
        cursor.execute("UPDATE reminders SET sms_sent = 1 WHERE id = %s", (reminder_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"status": "success", "reminder_id": reminder_id})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route("/send_sms", methods=["POST"])
def send_sms():
    data = request.json
    title = data.get("title")
    description = data.get("description")
    name = data.get("name")
    mobile = data.get("mobile")
    
    if not all([title, description, name, mobile]):
        return jsonify({"status": "error", "message": "Missing parameters"}), 400
    
    message = f"{title} - {description}"
    
    # Replace this URL with your actual SMS service endpoint
    sms_url = f"http://iotcloud.co.in/testsms/sms.php?sms=emr&name={name}&mess={message}&mobile={mobile}"
    
    try:
        response = requests.get(sms_url, timeout=10)
        if response.status_code == 200:
            return jsonify({"status": "success", "message": "SMS sent"})
        else:
            return jsonify({"status": "error", "message": f"Failed to send SMS, status {response.status_code}"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

# -------------------------------
# Check and Send Reminders
# -------------------------------
def check_reminders():
    with app.app_context():
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        now = datetime.now()
        now_str = now.strftime('%Y-%m-%d %H:%M')

        cursor.execute("""
            SELECT r.id, r.title, r.description, r.datetime, r.sent_count, r.sms_sent,
                   p.email, p.name, p.mobile
            FROM reminders r
            JOIN patients p ON r.patient_id = p.id
            WHERE r.sent_count < 3
            AND r.datetime <= %s
            AND r.datetime >= DATE_SUB(%s, INTERVAL 2 MINUTE)
        """, (now_str, now_str))
        reminders = cursor.fetchall()

        for reminder in reminders:
            # Send email
            send_reminder_email(reminder)
            # Increment sent_count
            cursor.execute("UPDATE reminders SET sent_count = sent_count + 1 WHERE id = %s", (reminder['id'],))
            conn.commit()

        cursor.close()
        conn.close()

# Scheduler to run every minute
scheduler = BackgroundScheduler()
scheduler.add_job(func=check_reminders, trigger="interval", minutes=1)
scheduler.start()

engine = pyttsx3.init()
engine.setProperty('rate', 150)
engine.setProperty('volume', 1)

# Load dementia dataset
dementia_df = pd.read_csv('dementia_knowledge.csv')

def get_dementia_answer(user_question):
    questions = dementia_df['question'].str.lower().tolist()
    match = get_close_matches(user_question.lower(), questions, n=1, cutoff=0.5)
    if match:
        row = dementia_df[dementia_df['question'].str.lower() == match[0]].iloc[0]
        return row['answer']
    return None

@app.route('/patient/chatbot')
def chatbot_page():
    if 'patient_id' not in session:
        return redirect(url_for('patient_login'))
    return render_template('chatbot.html')

@app.route('/patient/chatbot_query', methods=['POST'])
def chatbot_query():
    if 'patient_id' not in session:
        return jsonify({"response": "Please login first."})

    user_question = request.form.get('question', '').strip().lower()
    response_text = "Hello! How can I help you today?"

    if not user_question:
        return jsonify({"response": response_text})

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    now = datetime.now()

    # -----------------------------
    # 1️⃣ NEXT APPOINTMENT
    # -----------------------------
    if 'appointment' in user_question:
        cursor.execute("""
            SELECT title, description, datetime
            FROM reminders
            WHERE patient_id=%s
              AND title LIKE 'Appointment%%'
            ORDER BY datetime ASC
            LIMIT 1
        """, (session['patient_id'],))
        appt = cursor.fetchone()
        if appt:
            dt = appt['datetime'].strftime('%d %B %Y at %I:%M %p')
            response_text = f"Your next appointment is '{appt['title']}' on {dt}. {appt['description']}"
        else:
            response_text = "You have no upcoming appointments."

    # -----------------------------
    # 2️⃣ NEXT MEETING
    # -----------------------------
    elif 'meeting' in user_question:
        cursor.execute("""
            SELECT title, description, datetime
            FROM reminders
            WHERE patient_id=%s
              AND title LIKE 'Meeting%%'
            ORDER BY datetime ASC
            LIMIT 1
        """, (session['patient_id'],))
        meet = cursor.fetchone()
        if meet:
            dt = meet['datetime'].strftime('%d %B %Y at %I:%M %p')
            response_text = f"You have a meeting '{meet['title']}' on {dt}. {meet['description']}"
        else:
            response_text = "You have no upcoming meetings."

    # -----------------------------
    # 3️⃣ TABLET REMINDERS
    # -----------------------------
    elif 'tablet' in user_question or 'medicine' in user_question:
        cursor.execute("""
            SELECT title, description, datetime
            FROM reminders
            WHERE patient_id=%s
              AND title LIKE 'Tablet%%'
            ORDER BY datetime ASC
        """, (session['patient_id'],))
        tablets = cursor.fetchall()
        if tablets:
            response_text = "You need to take the following medicines:"
            for t in tablets:
                time_only = t['datetime'].strftime('%I:%M %p')
                response_text += f"\n• {t['title']} at {time_only}. {t['description']}"
        else:
            response_text = "You have no tablet reminders."

    # -----------------------------
    # 4️⃣ OTHER DEMENTIA QUESTIONS
    # -----------------------------
    else:
        dementia_answer = get_dementia_answer(user_question)
        if dementia_answer:
            response_text = dementia_answer
        else:
            response_text = (
                "I can help with dementia care, appointments, meetings, medicines, "
                "diet, behavior, and daily activities."
            )

    cursor.close()
    conn.close()
    return jsonify({"response": response_text})

UPLOAD_FOLDER = 'static/relatives'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# -------------------------------
# Games for patients
# -------------------------------
@app.route('/patient/games')
def games_dashboard():
    if 'patient_id' not in session:
        return redirect(url_for('patient_login'))
    return render_template('game_dashboard.html')

@app.route('/patient/games/attention', methods=['GET', 'POST'])
def attention_game():
    if 'patient_id' not in session:
        return redirect(url_for('patient_login'))    
    score = 0
    if request.method == 'POST':
        score = int(request.form.get('score', 0))
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO games_scores (patient_id, game_name, score) VALUES (%s,%s,%s)",
                       (session['patient_id'], 'Attention Game', score))
        conn.commit()
        cursor.close()
        conn.close()
        flash(f"Score saved: {score}")
        return redirect(url_for('games_dashboard'))
    
    return render_template('attention_game.html')

@app.route('/patient/memory_game', methods=['GET', 'POST'])
def memory_game():
    if 'patient_id' not in session:
        return redirect(url_for('patient_login'))

    video_file = url_for('static', filename='memory.mp4')
    correct_answers = ['ball', 'tree', 'cat', 'bottle']
    score = None   # 👈 IMPORTANT

    if request.method == 'POST':
        answers = request.form.getlist('answers')

        score = sum(
            1 for user_ans, correct_ans in zip(answers, correct_answers)
            if user_ans.lower().strip() == correct_ans.lower()
        )

        # Save to DB
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO games_scores (patient_id, game_name, score)
            VALUES (%s, %s, %s)
        """, (session['patient_id'], 'Memory Game', score))
        conn.commit()
        cursor.close()
        conn.close()

        # 👇 DO NOT REDIRECT
        return render_template(
            'memory_game.html',
            video_file=video_file,
            correct_answers=correct_answers,
            score=score
        )

    # GET request
    return render_template(
        'memory_game.html',
        video_file=video_file,
        correct_answers=correct_answers,
        score=score
    )

# =========================
# CONFIG
# =========================
MAX_IMAGES_PER_RELATIVE = 30
DATASET_DIR = "dataset/relatives"
MODEL_PATH = "relative_model.yml"

os.makedirs(DATASET_DIR, exist_ok=True)

camera = None
capture_active = False
current_relative_id = None
image_count = 0
lock = threading.Lock()

face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

# =========================
# TRAIN MODEL
# =========================
def train_relative_model():
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    faces = []
    labels = []

    if not os.path.exists(DATASET_DIR):
        return False

    for rel_id in os.listdir(DATASET_DIR):
        rel_path = os.path.join(DATASET_DIR, rel_id)
        if not os.path.isdir(rel_path):
            continue

        for img_name in os.listdir(rel_path):
            img_path = os.path.join(rel_path, img_name)
            gray = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
            if gray is None:
                continue

            faces.append(gray)
            labels.append(int(rel_id))

    # 🔒 SAFETY CHECK
    if len(faces) < 2:
        print("Not enough face data to train model")
        return False

    # ✅ THIS IS THE FIX
    labels = np.array(labels, dtype=np.int32)

    recognizer.train(faces, labels)
    recognizer.save(MODEL_PATH)
    print("Relative face model trained successfully")

    return True

# =========================
# ADD RELATIVE
# =========================
@app.route('/patient/relative/add', methods=['GET', 'POST'])
def add_relative():
    if 'patient_id' not in session:
        return redirect(url_for('patient_login'))

    if request.method == 'POST':
        name = request.form['name']
        relation = request.form['relation']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO patient_relatives (patient_id, relative_name, relation)
            VALUES (%s,%s,%s)
        """, (session['patient_id'], name, relation))
        conn.commit()
        rid = cursor.lastrowid
        cursor.close()
        conn.close()

        return redirect(url_for('train_relative_faces', relative_id=rid))

    return render_template('add_relative.html')

# =========================
# TRAIN RELATIVE FACES
# =========================
@app.route('/patient/relative/train/<int:relative_id>')
def train_relative_faces(relative_id):
    global camera, capture_active, current_relative_id, image_count

    image_count = 0
    capture_active = True
    current_relative_id = relative_id

    if camera:
        camera.release()

    camera = cv2.VideoCapture(0)
    return render_template('train_relative_faces.html')

@app.route('/patient/relative/video_feed')
def relative_video_feed():
    return Response(generate_relative_frames(),
        mimetype='multipart/x-mixed-replace; boundary=frame')

def generate_relative_frames():
    global camera, image_count, capture_active

    save_path = os.path.join(DATASET_DIR, str(current_relative_id))
    os.makedirs(save_path, exist_ok=True)

    while capture_active and image_count < MAX_IMAGES_PER_RELATIVE:
        success, frame = camera.read()
        if not success:
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            with lock:
                image_count += 1
                face_img = gray[y:y+h, x:x+w]
                cv2.imwrite(f"{save_path}/{image_count}.jpg", face_img)

            cv2.rectangle(frame, (x,y), (x+w,y+h), (0,255,0), 2)
            break

        ret, buffer = cv2.imencode('.jpg', frame)
        yield b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n'

        time.sleep(0.12)

    capture_active = False
    if camera:
        camera.release()

    train_relative_model()  # AUTO TRAIN AFTER CAPTURE

# =========================
# LIST RELATIVES
# =========================
@app.route('/patient/relatives')
def list_relatives():
    if 'patient_id' not in session:
        return redirect(url_for('patient_login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT id, relative_name, relation
        FROM patient_relatives
        WHERE patient_id = %s
        ORDER BY id DESC
    """, (session['patient_id'],))

    relatives = cursor.fetchall()
    cursor.close()
    conn.close()

    # ✅ Count images from dataset folder
    for r in relatives:
        rel_dir = os.path.join(DATASET_DIR, str(r['id']))
        if os.path.exists(rel_dir):
            r['images'] = len([
                f for f in os.listdir(rel_dir)
                if f.lower().endswith('.jpg')
            ])
        else:
            r['images'] = 0

    return render_template('relatives_list.html', relatives=relatives)

# =========================
# IDENTIFY RELATIVE (LIVE)
# =========================
@app.route('/patient/relative/identify')
def identify_relative():
    if 'patient_id' not in session:
        return redirect(url_for('patient_login'))
    return render_template('identify_relative.html')

@app.route('/patient/relative/identify_feed')
def identify_relative_feed():
    if 'patient_id' not in session:
        return redirect(url_for('patient_login'))

    patient_id = session['patient_id']  # ✅ capture early

    return Response(
        generate_identify_frames(patient_id),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )

def generate_identify_frames(patient_id):
    recognizer = cv2.face.LBPHFaceRecognizer_create()

    if not os.path.exists(MODEL_PATH):
        print("Model not found")
        return

    recognizer.read(MODEL_PATH)

    cam = cv2.VideoCapture(0)

    while True:
        success, frame = cam.read()
        if not success:
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            face_img = gray[y:y+h, x:x+w]
            label, confidence = recognizer.predict(face_img)

            name = "Unknown"
            color = (0, 0, 255)

            if confidence < 70:
                conn = get_db_connection()
                cursor = conn.cursor(dictionary=True)
                cursor.execute("""
                    SELECT relative_name, relation
                    FROM patient_relatives
                    WHERE id=%s AND patient_id=%s
                """, (int(label), patient_id))
                rel = cursor.fetchone()
                cursor.close()
                conn.close()

                if rel:
                    name = f"{rel['relative_name']} ({rel['relation']})"
                    color = (0, 255, 0)

            cv2.rectangle(frame, (x,y), (x+w,y+h), color, 2)
            cv2.putText(frame, name, (x, y-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

        ret, buffer = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' +
               buffer.tobytes() + b'\r\n')

    cam.release()
    
# -------------------------------
# Caregiver Routes
# -------------------------------
@app.route('/add', methods=['GET','POST'])
def add():
    if 'patient_id' not in session:
        return redirect(url_for('patient_login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        # Collect form data
        name = request.form['name']
        mobile = request.form['mobile']
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']

        # Hash the password
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        # Insert new caregiver into caregivers table
        cursor.execute("""
            INSERT INTO caregivers (name, mobile, email, username, password)
            VALUES (%s, %s, %s, %s, %s)
        """, (name, mobile, email, username, hashed_password))
        conn.commit()

        # Get the new caregiver ID
        caregiver_id = cursor.lastrowid

        # Link caregiver with current patient
        cursor.execute("""
            INSERT INTO patient_caregivers (patient_id, caregiver_id)
            VALUES (%s, %s)
        """, (session['patient_id'], caregiver_id))
        conn.commit()

        cursor.close()
        conn.close()
        flash("Caregiver added and linked successfully!")
        return redirect(url_for('patient_dashboard'))

    cursor.close()
    conn.close()
    return render_template('add.html')

@app.route('/caregiver/login', methods=['GET','POST'])
def caregiver_login():
    if request.method == 'POST':
        username = request.form['username']
        password = hashlib.sha256(request.form['password'].encode()).hexdigest()
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM caregivers WHERE username=%s AND password=%s",(username,password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        if user:
            session['caregiver_id'] = user['id']
            session['caregiver_name'] = user['name']
            return redirect(url_for('caregiver_dashboard'))
        else:
            flash("Invalid Credentials")
    return render_template('caregiver_login.html')

@app.route('/caregiver/dashboard')
def caregiver_dashboard():
    if 'caregiver_id' not in session:
        return redirect(url_for('caregiver_login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT p.*
        FROM patients p
        JOIN patient_caregivers pc ON p.id = pc.patient_id
        WHERE pc.caregiver_id = %s
    """, (session['caregiver_id'],))

    patients = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        'caregiver_dashboard.html',
        patients=patients
    )

@app.route('/caregiver/patient/<int:patient_id>')
def caregiver_patient_profile(patient_id):
    if 'caregiver_id' not in session:
        return redirect(url_for('caregiver_login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT p.*
        FROM patients p
        JOIN patient_caregivers pc ON p.id = pc.patient_id
        WHERE p.id = %s AND pc.caregiver_id = %s
    """, (patient_id, session['caregiver_id']))

    patient = cursor.fetchone()

    cursor.close()
    conn.close()

    if not patient:
        abort(403)  # forbidden

    return render_template(
        'patient_profile.html',
        patient=patient
    )

@app.route('/caregiver/patient/<int:patient_id>/tests')
def caregiver_patient_tests(patient_id):
    if 'caregiver_id' not in session:
        return redirect(url_for('caregiver_login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Authorization + data
    cursor.execute("""
        SELECT dt.*
        FROM dementia_tests dt
        JOIN patient_caregivers pc ON dt.patient_id = pc.patient_id
        WHERE dt.patient_id = %s AND pc.caregiver_id = %s
        ORDER BY dt.timestamp DESC
    """, (patient_id, session['caregiver_id']))

    tests = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        'patient_tests.html',
        tests=tests,
        patient_id=patient_id
    )

@app.route('/caregiver/patient/<int:patient_id>/chatbot')
def caregiver_patient_chatbot(patient_id):
    if 'caregiver_id' not in session:
        return redirect(url_for('caregiver_login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT cl.*
        FROM chatbot_logs cl
        JOIN patient_caregivers pc ON cl.patient_id = pc.patient_id
        WHERE cl.patient_id = %s AND pc.caregiver_id = %s
        ORDER BY cl.timestamp DESC
    """, (patient_id, session['caregiver_id']))

    logs = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        'patient_chatbot.html',
        logs=logs,
        patient_id=patient_id
    )

@app.route('/caregiver/patient/<int:patient_id>/activity')
def caregiver_patient_activity(patient_id):
    if 'caregiver_id' not in session:
        return redirect(url_for('caregiver_login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT la.*
        FROM login_activity la
        JOIN patient_caregivers pc ON la.user_id = pc.patient_id
        WHERE la.user_id = %s
          AND la.role = 'patient'
          AND pc.caregiver_id = %s
        ORDER BY la.login_time DESC
    """, (patient_id, session['caregiver_id']))

    activity = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        'patient_activity.html',
        activity=activity,
        patient_id=patient_id
    )

@app.route('/caregiver/patient/<int:patient_id>/games')
def caregiver_patient_games(patient_id):
    if 'caregiver_id' not in session:
        return redirect(url_for('caregiver_login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT gs.*
        FROM games_scores gs
        JOIN patient_caregivers pc ON gs.patient_id = pc.patient_id
        WHERE gs.patient_id = %s AND pc.caregiver_id = %s
        ORDER BY gs.played_at DESC
    """, (patient_id, session['caregiver_id']))

    games = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        'patient_games.html',
        games=games,
        patient_id=patient_id
    )

@app.route('/patient/<int:patient_id>/update_location', methods=['POST'])
def update_location(patient_id):
    data = request.json
    latitude = data.get('latitude')
    longitude = data.get('longitude')

    if latitude is None or longitude is None:
        return {"error": "Missing latitude or longitude"}, 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO patient_locations (patient_id, latitude, longitude)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE latitude=%s, longitude=%s, updated_at=CURRENT_TIMESTAMP
    """, (patient_id, latitude, longitude, latitude, longitude))

    conn.commit()
    cursor.close()
    conn.close()
    return {"status": "Location updated"}, 200

# Live location
@app.route('/caregiver/patient/<int:patient_id>/location')
def caregiver_patient_location(patient_id):
    if 'caregiver_id' not in session:
        return redirect(url_for('caregiver_login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True, buffered=True)

    cursor.execute("""
        SELECT latitude, longitude, updated_at
        FROM patient_locations
        WHERE patient_id=%s
    """, (patient_id,))
    location = cursor.fetchone()
    cursor.close()
    conn.close()

    if not location:
        location = {"latitude": 0, "longitude": 0, "updated_at": None}

    return render_template(
        'patient_location.html',
        patient_id=patient_id,
        patient_name="Patient Name Here",
        location=location,
        google_maps_api_key="your_actual_key"
    )

@app.route('/api/patient/<int:patient_id>/location')
def api_patient_location(patient_id):
    if 'caregiver_id' not in session:
        return {"error": "Unauthorized"}, 401

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT pl.latitude, pl.longitude
        FROM patient_locations pl
        JOIN patient_caregivers pc ON pl.patient_id = pc.patient_id
        WHERE pl.patient_id = %s AND pc.caregiver_id = %s
    """, (patient_id, session['caregiver_id']))

    location = cursor.fetchone()
    cursor.close()
    conn.close()

    if not location:
        return {"latitude": 0, "longitude": 0}

    return location

# -------------------------------
# Admin Routes
# -------------------------------
@app.route('/admin/login', methods=['GET','POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username=='admin' and password=='admin':
            session['admin'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            flash("Invalid Credentials")
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM patients")
    patients = cursor.fetchall()
    cursor.execute("SELECT * FROM caregivers")
    caregivers = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('admin_dashboard.html', patients=patients, caregivers=caregivers)

# -------------------------------
# Logout
# -------------------------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

# -------------------------------
# Run App
# -------------------------------
if __name__=="__main__":
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=check_reminders, trigger="interval", minutes=1)
    scheduler.start()
    app.run(debug=False)
