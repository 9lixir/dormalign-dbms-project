from flask import Flask, render_template, request, redirect, session
import psycopg2
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "secret123"

def get_db_connection():
    return psycopg2.connect(
        dbname="dormalign",
        user="postgres",
        password="1207",
        host="localhost",
        port="5432"
    )

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

        cur.execute("""
            INSERT INTO Student (name, gender, department, year, hostel_id)
            VALUES (%s, %s, %s, %s, %s) RETURNING student_id
        """, (name, gender, department, year, hostel_id))
        student_id = cur.fetchone()[0]

        cur.execute("""
            INSERT INTO Lifestyle_Preferences
            (student_id, sleep_time, cleanliness_level, noise_tolerance, guest_preference, study_style)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (student_id, sleep_time, cleanliness_level, noise_tolerance, guest_preference, study_style))

        cur.execute("""
            INSERT INTO Roommate_Request
            (student_id, preferred_room_type)
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
        FROM Student s
        JOIN Hostel h ON s.hostel_id = h.hostel_id
        LEFT JOIN Lifestyle_Preferences l ON s.student_id = l.student_id
        LEFT JOIN Roommate_Request r ON s.student_id = r.student_id
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
        WHERE s.student_id = %s
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

    student_id = session["user_id"]
    conn = get_db_connection()
    cur = conn.cursor()

    # Get current preferences
    cur.execute("SELECT * FROM lifestyle_preferences WHERE student_id=%s", (student_id,))
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