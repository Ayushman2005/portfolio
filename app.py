from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from flask import session, redirect, url_for
import pymysql
from datetime import datetime
import os
from dotenv import load_dotenv
import smtplib
from email.message import EmailMessage
load_dotenv()

app = Flask(__name__)
CORS(app)
app.secret_key = os.getenv("SECRET_KEY")
# MySQL Connection (Aiven)
def get_db_connection():
    return pymysql.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        cursorclass=pymysql.cursors.DictCursor,
        ssl={"ssl": {}}
    )
def send_email_notification(name, email, message):
    try:
        msg = EmailMessage()
        msg['Subject'] = '📩 New Contact Message'
        msg['From'] = os.getenv("SMTP_EMAIL")
        msg['To'] = os.getenv("ADMIN_EMAIL")

        msg.set_content(f"""
        You have received a new message from your portfolio website.

        Name: {name}
        Email: {email}

        Message:
        {message}
        """)

        with smtplib.SMTP(os.getenv("SMTP_SERVER"), int(os.getenv("SMTP_PORT"))) as server:
            server.starttls()
            server.login(
                os.getenv("SMTP_EMAIL"),
                os.getenv("SMTP_PASSWORD")
            )
            server.send_message(msg)

    except Exception as e:
        print("Email error:", e)

# ---------- ROUTES ----------

@app.route('/')
def index():
    return render_template('index.html')

# GET projects
@app.route('/api/projects', methods=['GET'])
def get_projects():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM projects ORDER BY created_at DESC")
        projects = cursor.fetchall()
        conn.close()
        return jsonify({"projects": projects})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ADD project
@app.route('/api/projects', methods=['POST'])
def add_project():
    try:
        data = request.json
        conn = get_db_connection()
        cursor = conn.cursor()

        sql = """
        INSERT INTO projects (title, description, technologies)
        VALUES (%s, %s, %s)
        """

        cursor.execute(sql, (
            data.get("title"),
            data.get("description"),
            ",".join(data.get("technologies", []))
        ))

        conn.commit()
        conn.close()
        return jsonify({"message": "Project added successfully"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# CONTACT form
@app.route('/api/contact', methods=['POST'])
def contact():
    try:
        data = request.json
        conn = get_db_connection()
        cursor = conn.cursor()

        sql = """
        INSERT INTO contacts (name, email, message)
        VALUES (%s, %s, %s)
        """

        cursor.execute(sql, (
            data.get('name'),
            data.get('email'),
            data.get('message')
        ))
        send_email_notification(
            data.get('name'),
            data.get('email'),
            data.get('message')
        )
        conn.commit()
        conn.close()
        return jsonify({"message": "Message sent successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# GET contacts
@app.route('/api/contacts', methods=['GET'])
def get_contacts():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM contacts ORDER BY created_at DESC")
        contacts = cursor.fetchall()
        conn.close()
        return jsonify({"contacts": contacts})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        data = request.json
        if (
            data.get('username') == os.getenv("ADMIN_USERNAME") and
            data.get('password') == os.getenv("ADMIN_PASSWORD")
        ):
            session['admin'] = True
            return jsonify({"message": "Login success"}), 200
        return jsonify({"message": "Invalid credentials"}), 401

    return render_template('admin_login.html')


@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin'):
        return redirect('/admin/login')
    return render_template('admin_dashboard.html')


@app.route('/admin/project', methods=['GET', 'POST'])
def admin_add_project():
    if not session.get('admin'):
        return jsonify({"error": "Unauthorized"}), 403

    try:
        data = request.json
        # Convert the string from the input field into a cleaned string for the DB
        tech_string = data.get('technologies', '') 
        
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO projects (title, description, technologies) VALUES (%s, %s, %s)",
            (data['title'], data['description'], tech_string)
        )

        conn.commit()
        conn.close()
        return jsonify({"message": "Project added"})
    except Exception as e:
        print(f"Error: {e}") # Look at your terminal to see the exact error
        return jsonify({"error": str(e)}), 500
@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    return redirect('/admin/login')
@app.route('/admin/projects')
def admin_projects():
    if not session.get('admin'):
        return redirect('/admin/login')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM projects ORDER BY created_at DESC")
    projects = cursor.fetchall()
    conn.close()

    return jsonify(projects)
@app.route('/admin/project/<int:id>', methods=['DELETE'])
def delete_project(id):
    if not session.get('admin'):
        return jsonify({"error": "Unauthorized"}), 403

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM projects WHERE id=%s", (id,))
    conn.commit()
    conn.close()

    return jsonify({"message": "Deleted"})
@app.route('/admin/messages')
def admin_messages():
    if not session.get('admin'):
        return redirect('/admin/login')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, name, email, message, created_at, is_read FROM contacts ORDER BY created_at DESC"
    )
    messages = cursor.fetchall()
    conn.close()

    return jsonify(messages)

@app.route('/admin/message/read/<int:id>', methods=['POST'])
def mark_message_read(id):
    if not session.get('admin'):
        return jsonify({"error": "Unauthorized"}), 403

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE contacts SET is_read = NOT is_read WHERE id=%s",
        (id,)
    )
    conn.commit()
    conn.close()

    return jsonify({"message": "Status updated"})
@app.route('/admin/message/<int:id>', methods=['DELETE'])
def delete_message(id):
    if not session.get('admin'):
        return jsonify({"error": "Unauthorized"}), 403

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM contacts WHERE id=%s", (id,))
    conn.commit()
    conn.close()

    return jsonify({"message": "Deleted"}), 200

@app.route('/admin/message/reply', methods=['POST'])
def reply_message():
    if not session.get('admin'):
        return jsonify({"error": "Unauthorized"}), 403

    data = request.json

    msg = EmailMessage()
    msg['Subject'] = "Reply from Portfolio Admin"
    msg['From'] = os.getenv("SMTP_EMAIL")
    msg['To'] = data['email']

    msg.set_content(data['reply'])

    with smtplib.SMTP(os.getenv("SMTP_SERVER"), int(os.getenv("SMTP_PORT"))) as server:
        server.starttls()
        server.login(os.getenv("SMTP_EMAIL"), os.getenv("SMTP_PASSWORD"))
        server.send_message(msg)

    return jsonify({"message": "Reply sent"})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
