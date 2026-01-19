from flask import Flask, render_template, request
import psycopg2

app = Flask(__name__)

def get_db_connection():
    conn = psycopg2.connect(
        dbname="dormalign",
        user="postgres",
        password="1207",
        host="localhost",
        port="5432"
    )
    return conn

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/roommate", methods=["GET", "POST"])
def roommate():
    if request.method == "POST":
        # student
        name = request.form.get("name")
        gender = request.form.get("gender")
        department = request.form.get("department")
        year = request.form.get("year")
        hostel_id = request.form.get("hostel_id")

        # life 
        sleep_time = request.form.get("sleep_time")
        cleanliness_level = request.form.get("cleanliness_level")
        noise_tolerance = request.form.get("noise_tolerance")
        guest_preference = request.form.get("guest_preference") == "True"
        study_style = request.form.get("study_style")

        # roommie 
        preferred_room_type = request.form.get("preferred_room_type")

        #inserting to db
        conn = get_db_connection()
        cur = conn.cursor()

        #student insert
        cur.execute("""
            INSERT INTO Student (name, gender, department, year, hostel_id)
            VALUES (%s, %s, %s, %s, %s) RETURNING student_id
        """, (name, gender, department, year, hostel_id))
        student_id = cur.fetchone()[0]

        # lifestyle ins
        cur.execute("""
            INSERT INTO Lifestyle_Preferences
            (student_id, sleep_time, cleanliness_level, noise_tolerance, guest_preference, study_style)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (student_id, sleep_time, cleanliness_level, noise_tolerance, guest_preference, study_style))

        # roomie req inser
        cur.execute("""
            INSERT INTO Roommate_Request
            (student_id, preferred_room_type)
            VALUES (%s, %s)
        """, (student_id, preferred_room_type))

        conn.commit()
        cur.close()
        conn.close()

        return "<h2>Form submitted successfully!</h2>"

    return render_template("roommate_form.html")

@app.route("/submissions")
def submissions():
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

@app.route("/dashboard/<int:student_id>")
def dashboard(student_id):
    conn = get_db_connection()
    cur = conn.cursor()

    # Fetch student info + hostel
    cur.execute("""
        SELECT s.name, s.department, s.year, h.hostel_name
        FROM student s
        JOIN hostel h ON s.hostel_id = h.hostel_id
        WHERE s.student_id = %s
    """, (student_id,))
    student_data = cur.fetchone()

    # Fetch lifestyle preferences
    cur.execute("""
        SELECT sleep_time, study_style, cleanliness_level, noise_tolerance
        FROM lifestyle_preferences
        WHERE student_id = %s
    """, (student_id,))
    preference_data = cur.fetchone()

    cur.close()
    conn.close()

    student = {
        "name": student_data[0],
        "department": student_data[1],
        "year": student_data[2],
        "hostel_name": student_data[3]
    }

    preferences = {
        "sleep_time": preference_data[0],
        "study_style": preference_data[1],
        "cleanliness_level": preference_data[2],
        "noise_tolerance": preference_data[3]
    }

    return render_template(
        "dashboard.html",
        student=student,
        preferences=preferences
    )

if __name__ == "__main__":
    app.run(debug=True,host="0.0.0.0",port=5001)