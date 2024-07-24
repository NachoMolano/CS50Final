import os

import sqlite3
from flask import Flask, flash, redirect, render_template, request, session, url_for, jsonify
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from flask_socketio import SocketIO, Namespace, send

from helpers import check_email

# Events element

events = []

# Configure App
app = Flask(__name__)

# Configure Session
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["TEMPLATES_AUTO_RELOAD"] = True
Session(app)
socketio = SocketIO(app)

# Connect SQL Database
def get_db_connection():
    conn = sqlite3.connect('schooler.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def index():
    if 'user_id' in session:
        return render_template("index.html", user=[session['username'], session['lastname']])
    return redirect("/login")

# Login and Signin
@app.route("/login", methods=["GET", "POST"])
def login():
    
    if 'user_id' in session:   
        return redirect("/")

    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("email"):
            flash("Must provide email")
            return redirect("/login")
        elif not check_email(request.form.get("email")):
            flash("Must provide a valid email")
            return redirect("/login")
        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("Must provide password")
            return redirect("/login")

        # Query database for username
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE email = ?", (request.form.get("email"),))
            rows = cursor.fetchall()

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            flash("Invalid email and/or password")
            return redirect("/login")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        session['username'] = rows[0]["name"]
        session['lastname'] = rows[0]['lastname']

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == 'POST':
        # check username and password
        name = request.form.get("name")
        lastname = request.form.get("lastname")
        email = request.form.get("email")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
            usedEmail = cursor.fetchall()
            
            if not name or not lastname:
                flash("Must provide name and last name")
                return redirect("/signup")
            elif not email:
                flash("Must provide email")
                return redirect("/signup")
            elif not check_email(email):
                flash("Must provide valid email")
                return redirect("/signup")
            elif usedEmail:
                flash("Email already in use")
                return redirect("/signup")
            elif not password:
                flash("Must provide a password")
                return redirect("/signup")
            elif not confirmation or password != confirmation:
                flash("Passwords do not match")
                return redirect("/signup")

            cursor = conn.cursor()
            cursor.execute("INSERT INTO users(name, lastname, email, hash) VALUES(?, ?, ?, ?)", (name, lastname, email, generate_password_hash(password),))
            conn.commit()
            
            cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
            row = cursor.fetchall()
            
        session["user_id"] = row[0]['id']
        session['username'] = row[0]["name"]
        session['lastname'] = row[0]['lastname']

        return redirect("/")
    else:
        return render_template("signup.html")


@app.route("/forgot")
def forgot():
    return render_template("forgot.html")

@app.route("/signout")
def signout():
    session.clear()
    return redirect("/login")


# Calendar

@app.route("/calendar")
def calendar():
    if 'user_id' not in session:
        return redirect("/login")
    
    events = []
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM events WHERE user_id=?", (session['user_id'],))
        eventRows = cursor.fetchall()

    for row in eventRows:
        events.append({
            'id': row['id'],
            'title': row['title'],
            'start': row['start'],
            'end': row['end'],
            'description': row['description'],
            'url': row['url'],
            'color': row['color']
        })
    
    return render_template("calendar.html", events=events, user=[session['username'], session['lastname']])

@app.route("/eventAdd", methods=["GET", "POST"])
def eventAdd():
    if request.method == "POST":
        title = request.form['title']
        startDate = request.form['startDate'] 
        startTime = request.form['startTime']
        endDate = request.form['endDate'] 
        endTime = request.form['endTime'] 
        url = request.form['url'] 
        allDay = request.form['hiddenAllDay']
        description = request.form['description']
        color = request.form['color']
        
        if endDate == '':
            endDate = startDate
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            if allDay == 'off':
                cursor.execute("INSERT INTO events(user_id, title, start, end, description, url, color) VALUES(?, ?, ?, ?, ?, ?, ?)", (session['user_id'], title, startDate + 'T' + startTime, endDate + 'T' + endTime, description, 'https://' + url, color))
            else:
                cursor.execute("INSERT INTO events(user_id, title, start, end, description, url, color) VALUES(?, ?, ?, ?, ?, ?, ?)", (session['user_id'], title, startDate, endDate, description, 'https://' + url, color))
            conn.commit()
            
    return redirect("/calendar")

@app.route("/delete", methods=["GET", "POST"])
def delete():
    if request.method == "POST":
        event_id = request.form['event_id']
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM events WHERE id = ?", (event_id,))
            conn.commit
        
    return redirect("/calendar")


# Grades

@app.route("/grades", methods=["GET", "POST"])
def grades():
    if 'user_id' not in session:   
        return redirect("/login")

    global subjects
    subjects=[]
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        rows = cursor.execute("SELECT * FROM subjects WHERE user_id=?", (session['user_id'],)).fetchall()
    
    
    for row in rows:
        subjects.append({
            'subject': row['subject'],
            'teacher': row['teacher'],
            'color': row['color'],
            'average': row['average']
        })
        
    return render_template("grades.html", subjects=subjects, user=[session['username'], session['lastname']])

@app.route("/subjectAdd", methods=["GET", "POST"])
def subjectAdd():
    if request.method == 'POST':
        subject = request.form['subject']
        teacher = request.form['teacher']
        color = request.form['color']
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            userSubjects = cursor.execute("SELECT subject FROM subjects WHERE user_id=?", (session['user_id'],)).fetchall()
            
            for row in userSubjects:
                if row['subject'] == subject:
                    flash("You already have that subject")
                    return redirect("/grades")
            
            cursor.execute("INSERT INTO subjects (user_id, subject, teacher, color) VALUES(?, ?, ?, ?)", (session["user_id"], subject, teacher, color))
            conn.commit()
    
    return redirect("/grades")

@app.route("/delete/<subject>", methods=["POST", "GET"])
def subjectDelete(subject):
    if request.method == "POST":
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM subjects WHERE subject_id=?", (subject,))
            conn.commit()
        return redirect("/grades")

@app.route('/grades/<subject>', methods=["POST", "GET"])
def show_grades(subject):
    if 'user_id' not in session:   
        return redirect("/login")
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        global currentSubject
        global suma
        cursor.execute("SELECT subject_id FROM subjects WHERE subject=? AND user_id=?", (subject, session['user_id']))
        currentSubject = cursor.fetchall()[0]['subject_id']
        
        
        if currentSubject:
            
            cursor.execute("SELECT SUM(percentage) FROM criteria WHERE subject_id=?", (currentSubject,))
            suma = cursor.fetchall()[0]['SUM(percentage)']
            if not suma:
                suma = 0
            
            cursor.execute("SELECT * FROM criteria WHERE subject_id=?", (currentSubject,))
            criteria = [dict(row) for row in cursor.fetchall()]
            
            cursor.execute("SELECT SUM((percentage*average)/100) FROM criteria WHERE subject_id=?", (currentSubject,))
            average = cursor.fetchall()[0]['SUM((percentage*average)/100)']
            
            if suma and average:
                cursor.execute("UPDATE subjects SET average=? WHERE subject_id=?", ((average/suma)*100, currentSubject))
            else:
                cursor.execute("UPDATE subjects SET average=? WHERE subject_id=?", (0, currentSubject))
            conn.commit()
            
            for crit in criteria:
                cursor.execute("SELECT * FROM grades WHERE criteria_id=?", (crit['criteria_id'],))
                crit['grades'] = cursor.fetchall()
            
            info = {
                'subject' : subject,
                'subject_id' : currentSubject,
                'average': average,
                'criteria' : criteria,
                'suma' : suma
            }
            return render_template("gradeinfo.html", info=info, user=[session['username'], session['lastname']])
        return redirect("/grades")

@app.route('/percentageAdd/<subject>', methods=["POST", "GET"])
def percentageAdd(subject):
    if request.method == "POST":
        criteria = request.form["criteria"]
        percentage = int(request.form["percentage"])       
        
        if suma != 0 and (suma + percentage) > 100:
            flash("Percentages must add to 100")
            return redirect(f"/grades/{subject}")
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO criteria (subject_id, criteria, percentage) VALUES (?, ?, ?)", (currentSubject, criteria, percentage))
            conn.commit()
            
    return redirect(f"/grades/{subject}")   

@app.route('/delete/<subject>/<criteria>', methods=["POST", "GET"])
def percentageDelete(subject, criteria):
    if request.method == "POST":
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM grades WHERE criteria_id=?", (criteria))
            cursor.execute("DELETE FROM criteria WHERE criteria_id=?", (criteria)) 
            conn.commit()
    return redirect(f"/grades/{subject}")

@app.route('/gradeAdd/<subject>/<criteria>', methods=["POST", "GET"])
def gradeAdd(subject, criteria):
        if request.method == "POST":
            with get_db_connection() as conn:
                cursor = conn.cursor()
                task = request.form["task"]
                grade = int(request.form["grade"])
                
                cursor.execute("INSERT INTO grades (criteria_id, task, grade) VALUES (? ,? ,?)", (criteria, task, grade))
                
                cursor.execute("SELECT AVG(grade) FROM grades WHERE criteria_id=?", (criteria,))
                avg = cursor.fetchall()[0]['AVG(grade)']
                cursor.execute("UPDATE criteria SET average=? WHERE criteria_id=?", (avg, criteria))
                
                conn.commit()
            
        return redirect(f"/grades/{subject}")
    
@app.route('/delete/<subject>/<criteria>/<grade>', methods=["POST", "GET"])
def gradeDelete(subject, criteria, grade):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM grades WHERE id=?", (int(grade),))
        conn.commit()
    return redirect(f"/grades/{subject}")
 
# Chat
@app.route('/chat')
def render_chat():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name, lastname FROM users WHERE id<>?", (session['user_id'],))
        members = [dict(row) for row in cursor.fetchall()]
    return render_template('chat.html', user=[session['username'], session['lastname']], members=members)

@app.route("/messages")
def display_messages():
    conn = get_db_connection()
    messages = conn.execute("SELECT content, user_id, username, timestamp FROM messages ORDER BY timestamp ASC").fetchall()
    conn.close()
    return jsonify(messages=[dict(row) for row in messages], current_user=session['user_id'])
                   
                   
class chatNamespace(Namespace):
    def on_message(self, msg):
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO messages (content, user_id, username, timestamp) VALUES (?, ?, ?, datetime('now', 'localtime'))", (msg, session['user_id'], session['username']))
            conn.commit()
            send(msg, broadcast=True, namespace='/chat')

socketio.on_namespace(chatNamespace('/chat'))
 
if __name__ == "__main__":
    socketio.run(app, debug=True, port=5000)