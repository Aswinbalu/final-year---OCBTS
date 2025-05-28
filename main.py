from flask import Flask, render_template, redirect, request, session, url_for, jsonify
import mysql.connector
import random
import json
import re
import datetime
from googletrans import Translator
from urllib.parse import quote

app = Flask(__name__, static_url_path='/static')
app.secret_key = 'abcdef'

# Database connection
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    charset="utf8",
    database="railway_booking"
)

# Load Intents
json_file_path = 'D:/booking_bot/nlp_pipeline/training data/intents.json'

def load_intents():
    with open(json_file_path, 'r') as f:
        return json.load(f)

intents = load_intents()

# Translator
translator = Translator()

# Email Helper Function
def send_email_via_iframe(email, subject, message):
    """Helper function to send email using the iframe approach"""
    encoded_message = quote(message)
    encoded_subject = quote(subject)
    
    iframe_html = f"""
    <iframe src="http://iotcloud.co.in/testmail/testmail1.php?message={encoded_message}&email={email}&subject={encoded_subject}" 
            width="10" height="10" frameborder="0" style="display:none;"></iframe>
    """
    return iframe_html  # <-- FIXED


# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin', methods=['POST', 'GET'])
def admin():
    msg = ""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor = mydb.cursor()
        cursor.execute('SELECT * FROM admin WHERE username = %s AND password = %s', (username, password))
        account = cursor.fetchone()
        
        if account:
            session['username'] = username
            session['user_type'] = 'admin'
            msg = "success"
            return redirect(url_for('train'))
        else:
            msg = "fail"
    return render_template('admin.html', msg=msg)

@app.route('/login', methods=['POST', 'GET'])
def login():
    msg = ""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor = mydb.cursor()
        cursor.execute('SELECT * FROM user WHERE username = %s AND password = %s', (username, password))
        account = cursor.fetchone()
        
        if account:
            session['username'] = username
            session['user_type'] = 'user'
            msg = "success"
            return redirect(url_for('bot'))
        else:
            msg = "fail"
    return render_template('login.html', msg=msg)

@app.route('/register', methods=['POST', 'GET'])
def register():
    msg = ""
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        mobile = request.form['mobile']
        username = request.form['username']
        password = request.form['password']

        now = datetime.datetime.now()
        date_join = now.strftime("%Y-%m-%d")
        cursor = mydb.cursor()

        cursor.execute("SELECT count(*) FROM user where username=%s", (username,))
        cnt = cursor.fetchone()[0]
        if cnt == 0:
            cursor.execute("SELECT max(id)+1 FROM user")
            maxid = cursor.fetchone()[0]
            if maxid is None:
                maxid = 1
            sql = "INSERT INTO user(id, name, email, mobile, username, password, date_join) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            val = (maxid, name, email, mobile, username, password, date_join)
            cursor.execute(sql, val)
            mydb.commit()
            msg = "success"
            return redirect(url_for('login'))
        else:
            msg = "fail"
    return render_template('register.html', msg=msg)

@app.route('/train', methods=['GET', 'POST'])
def train():
    message = ''
    if request.method == 'POST':
        data = request.form
        cursor = mydb.cursor()
        cursor.execute(""" 
            INSERT INTO transport (id, transport_type, transport_name, source, destination, departure_time, arrival_time, fare, transport_number) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            random.randint(1000, 9999),
            data['transport_type'],
            data['transport_name'],
            data['source'],
            data['destination'],
            data['departure_time'],
            data['arrival_time'],
            data['fare'],
            data['transport_number']
        ))
        mydb.commit()
        cursor.close()
        message = f"{data['transport_type'].title()} '{data['transport_name']}' added successfully!"
    return render_template("train.html", message=message)

@app.route('/bot', methods=['GET', 'POST'])
def bot():
    if request.method == 'POST':
        user_message = request.json.get('message', '')
        try:
            response = handle_user_message(user_message)
            return jsonify({"response": response})
        except Exception as e:
            print("Error:", e)
            return jsonify({"response": "⚠️ Internal error occurred."})
    return render_template('bot.html')

def handle_user_message(message):
    if not message:
        return "Please enter a message."

    message_lower = message.lower()

    # Match "from X to Y"
    match = re.search(r"from (.+) to (.+)", message_lower)
    if match:
        source = match.group(1).strip().title()
        destination = match.group(2).strip().title()
        return search_transport(source, destination)

    # Match "between X and Y"
    match = re.search(r"between (.+) and (.+)", message_lower)
    if match:
        source = match.group(1).strip().title()
        destination = match.group(2).strip().title()
        return search_transport(source, destination)

    # Match booking
    match = re.search(r"book (.+) for (\d+) passengers? on (\d{4}-\d{2}-\d{2})", message_lower)
    if match:
        transport_name = match.group(1).strip().title()
        passenger_count = int(match.group(2))
        date = match.group(3)
        return book_ticket(transport_name, passenger_count, date)

    # Match status
    match = re.search(r"(status|track).*(book|ticket).*?(book-\d+)", message_lower)
    if match:
        booking_id = match.group(3).upper()
        return check_ticket_status(booking_id)

    # Match cancel
    match = re.search(r"cancel.*?(book-\d+)", message_lower)
    if match:
        booking_id = match.group(1).upper()
        return cancel_ticket(booking_id)

    # Fallback: intent.json
    for intent in intents['intents']:
        for pattern in intent['patterns']:
            pattern_clean = re.sub(r"\{.*?\}", "", pattern.lower()).strip()
            if pattern_clean and pattern_clean in message_lower:
                response_template = random.choice(intent['responses'])
                return fill_placeholders(response_template, message)

    return "❓ Sorry, I didn't understand that. Try asking about booking, transport, or status."

def fill_placeholders(response_template, user_message):
    match = re.search(r"(book-\d+)", user_message)
    if match:
        response_template = response_template.replace("{booking_id}", match.group(1))

    match = re.search(r"from (.+) to (.+)", user_message)
    if match:
        response_template = response_template.replace("{source}", match.group(1).title())
        response_template = response_template.replace("{destination}", match.group(2).title())

    match = re.search(r"between (.+) and (.+)", user_message)
    if match:
        response_template = response_template.replace("{source}", match.group(1).title())
        response_template = response_template.replace("{destination}", match.group(2).title())

    match = re.search(r"book (.+) for (\d+) passengers? on (\d{4}-\d{2}-\d{2})", user_message.lower())
    if match:
        response_template = response_template.replace("{transport_name}", match.group(1).title())
        response_template = response_template.replace("{passenger_count}", match.group(2))
        response_template = response_template.replace("{date}", match.group(3))
        response_template = response_template.replace("{booking_id}", f"BOOK-{random.randint(1000,9999)}")

    return response_template

def search_transport(source, destination):
    cursor = mydb.cursor(dictionary=True)
    cursor.execute("SELECT * FROM transport WHERE source=%s AND destination=%s", (source, destination))
    rows = cursor.fetchall()
    cursor.close()

    if not rows:
        return f"No transport options found from {source} to {destination}."

    response = f"🚆 Available transport from {source} to {destination}:\n"
    transport_types = {}
    for row in rows:
        transport_type = row.get('transport_type', '').title()
        if transport_type not in transport_types:
            transport_types[transport_type] = []
        transport_types[transport_type].append(row)

    for transport_type, transport_list in transport_types.items():
        response += f"\n{transport_type} Options:\n"
        for i, transport in enumerate(transport_list, start=1):
            transport_name = transport.get('transport_name', 'Unknown')
            transport_number = transport.get('transport_number', 'N/A')
            departure_time = transport.get('departure_time', 'N/A')
            arrival_time = transport.get('arrival_time', 'N/A')
            fare = transport.get('fare', 'N/A')

            response += f"{i}. {transport_name} (No: {transport_number}), Departs: {departure_time}, Arrives: {arrival_time}, Fare: ₹{fare}\n"

    return response

def book_ticket(transport_name, passenger_count, travel_date):
    cursor = mydb.cursor()

    # Check if user is logged in
    if 'username' not in session:
        return "You need to be logged in to book tickets."

    # Get user email
    user_cursor = mydb.cursor()
    user_cursor.execute("SELECT email FROM user WHERE username = %s", (session['username'],))
    user_result = user_cursor.fetchone()
    
    if not user_result:
        return "User not found."
    
    user_email = user_result[0]
    user_cursor.close()

    # Get transport details
    cursor.execute("SELECT id, transport_number, fare FROM transport WHERE transport_name = %s", (transport_name,))
    transport_result = cursor.fetchone()

    if not transport_result:
        return f"Transport '{transport_name}' not found."

    transport_id, transport_number, fare = transport_result
    total_fare = fare * passenger_count

    # Generate booking ID
    booking_id = f"BOOK-{random.randint(1000, 9999)}"
    
    # Insert booking
    cursor.execute(""" 
        INSERT INTO bookings (booking_id, transport_id, transport_number, travel_date, passengers, status, total_fare, user_email) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (booking_id, transport_id, transport_number, travel_date, passenger_count, "Confirmed", total_fare, user_email))
    mydb.commit()
    cursor.close()

    # Prepare email content
    email_subject = f"Booking Confirmation - {booking_id}"
    email_message = f"""
    Your booking has been confirmed!

    Booking ID: {booking_id}
    Transport: {transport_name} (No: {transport_number})
    Date: {travel_date}
    Passengers: {passenger_count}
    Total Fare: ₹{total_fare}

    Thank you for using our service!
    """

    # Generate email iframe
    send_email_via_iframe(user_email, email_subject, email_message)

    # Return response
    response = f"""
    🎟️ Booking confirmed!
    Booking ID: {booking_id}
    Transport: {transport_name} (No: {transport_number})
    Date: {travel_date}
    Passengers: {passenger_count}
    Total Fare: ₹{total_fare}

    
    """

    return response

def check_ticket_status(booking_id):
    cursor = mydb.cursor(dictionary=True)
    cursor.execute(""" 
        SELECT b.booking_id, b.status, t.transport_name, b.travel_date, b.passengers, b.total_fare
        FROM bookings b 
        JOIN transport t ON b.transport_id = t.id 
        WHERE b.booking_id = %s
    """, (booking_id,))
    result = cursor.fetchone()
    cursor.close()

    if not result:
        return "No booking found with that ID."

    return (f"📄 Booking ID: {result['booking_id']}\n"
            f"Transport: {result['transport_name']}\n"
            f"Date: {result['travel_date']}\n"
            f"Passengers: {result['passengers']}\n"
            f"Total Fare: ₹{result['total_fare']}\n"
            f"Status: {result['status']}")

def cancel_ticket(booking_id):
    cursor = mydb.cursor(dictionary=True)

    # Check if user is logged in
    if 'username' not in session:
        return "You need to be logged in to cancel tickets."

    # Get booking details and verify ownership
    cursor.execute("""
        SELECT b.*, t.transport_name 
        FROM bookings b
        JOIN transport t ON b.transport_id = t.id
        WHERE b.booking_id = %s AND b.user_email = (
            SELECT email FROM user WHERE username = %s
        )
    """, (booking_id, session['username']))
    booking = cursor.fetchone()

    if not booking:
        return "No booking found or you don't have permission to cancel this booking."

    # Update status to cancelled
    cursor.execute("UPDATE bookings SET status='Cancelled' WHERE booking_id=%s", (booking_id,))
    mydb.commit()
    affected = cursor.rowcount
    cursor.close()

    if affected > 0:
        # Prepare cancellation email
        email_subject = f"Booking Cancelled - {booking_id}"
        email_message = f"""
        Your booking has been cancelled.

        Booking ID: {booking_id}
        Transport: {booking['transport_name']} (No: {booking['transport_number']})
        Date: {booking['travel_date']}
        Passengers: {booking['passengers']}
        Refund Amount: ₹{booking['total_fare']}

        We hope to serve you again in the future!
        """

        # Generate email iframe
        send_email_via_iframe(booking['user_email'], email_subject, email_message)

        # Return response
        response = f"""
        ❌ Booking cancelled successfully!
        Booking ID: {booking_id}
        Refund Amount: ₹{booking['total_fare']}

        
        """ 

        return response
    
    return "Failed to cancel booking."

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)
