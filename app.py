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

if __name__ == "__main__":
    app.run(debug=True,host="0.0.0.0",port=5001)