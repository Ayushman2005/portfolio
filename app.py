from flask import Flask, render_template, request, jsonify, session, redirect
from flask_cors import CORS
import pymysql
from datetime import datetime
import os
import requests
from dotenv import load_dotenv

# ---------------- CONFIG ----------------
load_dotenv()

app = Flask(__name__)
CORS(app)

app.secret_key = os.getenv("SECRET_KEY")

# ---------------- DATABASE ----------------
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

# ---------------- EMAILJS ----------------
def send_email_notification(name, email, message):
    try:
        url = "https://api.emailjs.com/api/v1.0/email/send"
        payload = {
            "service_id": os.getenv("EMAILJS_SERVICE_ID"),
            "template_id": os.getenv("EMAILJS_NOTIFY_TEMPLATE_ID"),
            "user_id": os.getenv("EMAILJS_PUBLIC_KEY"),
            "template_params": {
                "from_name": name,
                "from_email": email,
                "message": message
            }
        }
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print("EmailJS notify error:", e)

# ---------------- ROUTES ----------------
@app.route('/')
def index():
    return render_template('index.html')

# ---------- PROJECTS API ----------
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


@app.route('/api/projects', methods=['POST'])
def add_project():
    try:
        data = request.json
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO projects (title, description, technologies) VALUES (%s, %s, %s)",
            (
                data.get("title"),
                data.get("description"),
                ",".join(data.get("technologies", []))
            )
        )

        conn.commit()
        conn.close()
        return jsonify({"message": "Project added successfully"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------- CONTACT FORM ----------
@app.route('/api/contact', methods=['POST'])
def contact():
    try:
        data = request.json
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO contacts (name, email, message) VALUES (%s, %s, %s)",
            (
                data.get('name'),
                data.get('email'),
                data.get('message')
            )
        )

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


# ---------- ADMIN AUTH ----------
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


@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    return redirect('/admin/login')


@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin'):
        return redirect('/admin/login')
    return render_template('admin_dashboard.html')


# ---------- ADMIN PROJECTS ----------
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


# ---------- ADMIN MESSAGES ----------
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
    cursor.execute("UPDATE contacts SET is_read = NOT is_read WHERE id=%s", (id,))
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


# ---------- ADMIN REPLY (EmailJS) ----------
@app.route('/admin/message/reply', methods=['POST'])
def reply_message():
    if not session.get('admin'):
        return jsonify({"error": "Unauthorized"}), 403

    data = request.json

    try:
        url = "https://api.emailjs.com/api/v1.0/email/send"
        payload = {
            "service_id": os.getenv("EMAILJS_SERVICE_ID"),
            "template_id": os.getenv("EMAILJS_REPLY_TEMPLATE_ID"),
            "user_id": os.getenv("EMAILJS_PUBLIC_KEY"),
            "template_params": {
                "to_email": data['email'],
                "reply_message": data['reply']
            }
        }
        requests.post(url, json=payload, timeout=10)
        return jsonify({"message": "Reply sent"}), 200

    except Exception as e:
        print("EmailJS reply error:", e)
        return jsonify({"error": "Failed to send reply"}), 500


# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=False, port=5000)
