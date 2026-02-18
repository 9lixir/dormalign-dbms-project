from flask import Flask, render_template, request, redirect, session
import os
import psycopg2
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY")


def get_db_connection():
    database_url = os.environ.get("DATABASE_URL")
    if database_url:
        return psycopg2.connect(database_url)
    else:
        return psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT")
        )


def get_student_id_by_user_id(cur, user_id):
    cur.execute("SELECT student_id FROM student WHERE user_id = %s", (user_id,))
    row = cur.fetchone()
    return row[0] if row else None


def is_admin():
    if "user_id" not in session:
        return False
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT role FROM users WHERE id = %s", (session["user_id"],))
    user = cur.fetchone()
    cur.close()
    conn.close()
    return user is not None and user[0] == "admin"

#compat scores calculation

def calculate_compatibility(s1,s2):
    score = 0
    if s1["sleep_time"] == s2["sleep_time"]:
        score += 25

    if s1["study_style"] == s2["study_style"]:
        score += 20

    if abs(int(s1["cleanliness_level"]) - int(s2["cleanliness_level"])) <= 1:
        score += 20

    if abs(int(s1["noise_tolerance"]) - int(s2["noise_tolerance"])) <= 1:
        score += 20

    if s1["guest_preference"] == s2["guest_preference"]:
        score += 15

    return score


@app.route("/")
def home():
    if "user_id" not in session:
        return render_template("index.html", user_type=None)

    if is_admin():
        user_type = "admin"
    else:
        user_type = "student"

    return render_template("index.html", user_type=user_type)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = generate_password_hash(request.form["password"])
        email = request.form["email"]

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO users (username, password,email) VALUES (%s, %s,%s)",
            (username, password,email)
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
                INSERT INTO roommate_request (student_id, preferred_room_type, request_status)
                VALUES (%s, %s, %s)
            """, (student_id, preferred_room_type, "Pending"))

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

@app.route("/admin/calculate_compatibility")
def generate_compatibility():
    if not is_admin():
        return "Access Denied", 403
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("delete from compatibility_score")

    cur.execute("""select s.student_id,s.gender,s.hostel_id,
                lp.sleep_time,lp.cleanliness_level,
                lp.noise_tolerance, lp.guest_preference,
                lp.study_style 
                from student s join lifestyle_preferences lp
                on s.student_id =lp.student_id
                join roommate_request rr on s.student_id = rr.student_id
                where rr.preferred_room_type != 'Single'""")
    
    students = cur.fetchall()
    student_list = []

    for row in students:
        student={
            "student_id": row[0],
            "gender": row[1],
            "hostel_id": row[2],
            "sleep_time": row[3],
            "cleanliness_level": row[4],
            "noise_tolerance": row[5],
            "guest_preference": row[6],
            "study_style": row[7],
        }
        student_list.append(student)
    
    for i in range(len(student_list)):
        for j in range(i+1, len(student_list)):
            s1 = student_list[i]
            s2 = student_list[j]

            #these are conditions that must be fulfilled before any compat scores are calculated
            if s1["gender"] != s2["gender"]:
                continue
            if s1["hostel_id"] != s2["hostel_id"]:
                continue

            score = calculate_compatibility(s1,s2)

            cur.execute("""Insert into compatibility_score
                        (student1_id,student2_id,compatibility_score,calculated_date)
                        values (%s,%s,%s, NOW())""",
                        (s1["student_id"], s2["student_id"], score))
    
    conn.commit()
    cur.close()
    conn.close()
    return "Scores calculated successfully"

@app.route("/admin/view/compatibility")
def view_compatibility():
    if not is_admin():
        return "Access Denied", 403
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT c.score_id, s1.name AS student1, s2.name AS student2, c.compatibility_score, c.calculated_date,
            rr1.assigned_roommate_id AS s1_assigned,
            rr2.assigned_roommate_id AS s2_assigned,
            s1.student_id AS s1_id,
            s2.student_id AS s2_id
        FROM compatibility_score c
        JOIN student s1 ON c.student1_id = s1.student_id
        JOIN student s2 ON c.student2_id = s2.student_id
        LEFT JOIN roommate_request rr1 ON s1.student_id = rr1.student_id
        LEFT JOIN roommate_request rr2 ON s2.student_id = rr2.student_id
        ORDER BY c.compatibility_score DESC
    """)
    scores = cur.fetchall()
    cur.close()
    conn.close()

    return render_template("admin_compatibility.html", scores=scores)

@app.route("/admin/assign_roommates/<int:s1_id>/<int:s2_id>", methods=["POST"])
def assign_roommate_pair(s1_id, s2_id):
    if not is_admin():
        return "Access Denied", 403

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT assigned_roommate_id FROM roommate_request
        WHERE student_id = %s
        """, (s1_id,))
    s1_assigned = cur.fetchone()

    cur.execute("""
        SELECT assigned_roommate_id FROM roommate_request
        WHERE student_id = %s
        """, (s2_id,))
    s2_assigned = cur.fetchone()

    if (s1_assigned and s1_assigned[0]) or (s2_assigned and s2_assigned[0]):
        cur.close()
        conn.close()
        return "One of the students is already assigned!", 400
    
    cur.execute("""
        UPDATE roommate_request
        SET assigned_roommate_id = %s, request_status='Assigned'
        WHERE student_id = %s
        """, (s2_id, s1_id))
    cur.execute("""
        UPDATE roommate_request
        SET assigned_roommate_id = %s, request_status='Assigned'
        WHERE student_id = %s
        """, (s1_id, s2_id))

    conn.commit()
    cur.close()
    conn.close()
    return redirect("/admin/view/compatibility")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
