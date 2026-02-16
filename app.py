from flask import Flask, render_template, request, redirect, session
import os
import psycopg2
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "secret123")


def get_db_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME", "dormalign"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "1207"),
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432")
    )


def get_student_id_by_user_id(cur, user_id):
    cur.execute("SELECT student_id FROM student WHERE user_id = %s", (user_id,))
    row = cur.fetchone()
    return row[0] if row else None
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = generate_password_hash(request.form["password"])

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO users (username, password) VALUES (%s, %s)",
            (username, password)
        )
        conn.commit()
        cur.close()
        conn.close()

        return redirect("/login")

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT id, password FROM users WHERE username = %s",
            (username,)
        )
        user = cur.fetchone()
        cur.close()
        conn.close()

        if user and check_password_hash(user[1], password):
            session["user_id"] = user[0]
            return redirect("/")
        return redirect("/login")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/roommate", methods=["GET", "POST"])
def roommate():
    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":
        name = request.form.get("name")
        gender = request.form.get("gender")
        department = request.form.get("department")
        year = request.form.get("year")
        hostel_id = request.form.get("hostel_id")

        sleep_time = request.form.get("sleep_time")
        cleanliness_level = request.form.get("cleanliness_level")
        noise_tolerance = request.form.get("noise_tolerance")
        guest_preference = request.form.get("guest_preference") == "True"
        study_style = request.form.get("study_style")

        preferred_room_type = request.form.get("preferred_room_type")

        conn = get_db_connection()
        cur = conn.cursor()

        user_id = session["user_id"]
        student_id = get_student_id_by_user_id(cur, user_id)

        if student_id:
            cur.execute("""
                UPDATE student
                SET name = %s, gender = %s, department = %s, year = %s, hostel_id = %s
                WHERE student_id = %s
            """, (name, gender, department, year, hostel_id, student_id))
        else:
            cur.execute("""
                INSERT INTO student (user_id, name, gender, department, year, hostel_id)
                VALUES (%s, %s, %s, %s, %s, %s) RETURNING student_id
            """, (user_id, name, gender, department, year, hostel_id))
            student_id = cur.fetchone()[0]

        cur.execute("""
            INSERT INTO lifestyle_preferences
            (student_id, sleep_time, cleanliness_level, noise_tolerance, guest_preference, study_style)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (student_id)
            DO UPDATE SET
                sleep_time = EXCLUDED.sleep_time,
                cleanliness_level = EXCLUDED.cleanliness_level,
                noise_tolerance = EXCLUDED.noise_tolerance,
                guest_preference = EXCLUDED.guest_preference,
                study_style = EXCLUDED.study_style
        """, (student_id, sleep_time, cleanliness_level, noise_tolerance, guest_preference, study_style))

        cur.execute("SELECT request_id FROM roommate_request WHERE student_id = %s", (student_id,))
        request_row = cur.fetchone()
        if request_row:
            cur.execute("""
                UPDATE roommate_request
                SET preferred_room_type = %s
                WHERE request_id = %s
            """, (preferred_room_type, request_row[0]))
        else:
            cur.execute("""
                INSERT INTO roommate_request (student_id, preferred_room_type)
                VALUES (%s, %s)
            """, (student_id, preferred_room_type))

        conn.commit()
        cur.close()
        conn.close()

        return redirect("/dashboard")

    return render_template("roommate_form.html")

@app.route("/submissions")
def submissions():
    if "user_id" not in session:
        return redirect("/login")

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT s.student_id, s.name, s.gender, s.department, s.year, h.hostel_name,
               l.sleep_time, l.cleanliness_level, l.noise_tolerance, l.guest_preference, l.study_style,
               r.preferred_room_type
        FROM student s
        JOIN hostel h ON s.hostel_id = h.hostel_id
        LEFT JOIN lifestyle_preferences l ON s.student_id = l.student_id
        LEFT JOIN roommate_request r ON s.student_id = r.student_id
    """)
    students = cur.fetchall()
    cur.close()
    conn.close()

    return render_template("submissions.html", students=students)

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/login")

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT s.student_id, s.name, s.department, s.year, h.hostel_name,
               l.sleep_time, l.study_style, l.cleanliness_level, l.noise_tolerance
        FROM student s
        JOIN hostel h ON s.hostel_id = h.hostel_id
        LEFT JOIN lifestyle_preferences l ON s.student_id = l.student_id
        WHERE s.user_id = %s
    """, (session["user_id"],))
    
    data = cur.fetchone()
    cur.close()
    conn.close()

    if not data:
        return "<h2>No data found for this user.</h2>"

    student = {
        "student_id": data[0],
        "name": data[1],
        "department": data[2],
        "year": data[3],
        "hostel_name": data[4]
    }

    preferences = {
        "sleep_time": data[5],
        "study_style": data[6],
        "cleanliness_level": data[7],
        "noise_tolerance": data[8]
    }

    return render_template("dashboard.html", student=student, preferences=preferences)

@app.route("/update_preferences", methods=["GET", "POST"])
def update_preferences():
    if "user_id" not in session:
        return redirect("/login")

    conn = get_db_connection()
    cur = conn.cursor()
    student_id = get_student_id_by_user_id(cur, session["user_id"])

    if not student_id:
        cur.close()
        conn.close()
        return redirect("/roommate")

    # Get current preferences
    cur.execute("""
        SELECT sleep_time, cleanliness_level, noise_tolerance, guest_preference, study_style
        FROM lifestyle_preferences
        WHERE student_id = %s
    """, (student_id,))
    pref = cur.fetchone()

    if request.method == "POST":
        sleep_time = request.form.get("sleep_time")
        cleanliness_level = request.form.get("cleanliness_level")
        noise_tolerance = request.form.get("noise_tolerance")
        guest_preference = request.form.get("guest_preference") == "True"
        study_style = request.form.get("study_style")

        # Update preferences
        if pref:
            cur.execute("""
                UPDATE lifestyle_preferences
                SET sleep_time=%s, cleanliness_level=%s, noise_tolerance=%s,
                    guest_preference=%s, study_style=%s
                WHERE student_id=%s
            """, (sleep_time, cleanliness_level, noise_tolerance, guest_preference, study_style, student_id))
        else:
            cur.execute("""
                INSERT INTO lifestyle_preferences (student_id, sleep_time, cleanliness_level, noise_tolerance, guest_preference, study_style)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (student_id, sleep_time, cleanliness_level, noise_tolerance, guest_preference, study_style))

        conn.commit()
        cur.close()
        conn.close()
        return redirect("/dashboard")

    cur.close()
    conn.close()
    return render_template("update_preferences.html", pref=pref)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
