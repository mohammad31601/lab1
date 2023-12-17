from flask import Flask, render_template, request, jsonify, g, redirect, url_for
import mysql.connector

app = Flask(__name__)

# Database configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'jiblab1'

# Function to get a MySQL connection
def get_mysql_connection():
    if 'mysql_connection' not in g:
        g.mysql_connection = mysql.connector.connect(
            host=app.config['MYSQL_HOST'],
            user=app.config['MYSQL_USER'],
            password=app.config['MYSQL_PASSWORD'],
            database=app.config['MYSQL_DB'],
            port=3306
        )
    return g.mysql_connection

# Close the MySQL connection at the end of each request
@app.teardown_appcontext
def close_mysql_connection(e=None):
    mysql_connection = g.pop('mysql_connection', None)
    if mysql_connection is not None:
        mysql_connection.close()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        return submit_form()

    cursor = get_mysql_connection().cursor(dictionary=True)

    # Query for Stage 1
    query1 = """SELECT * from battery_rul"""
    cursor.execute(query1)
    query1_output = cursor.fetchall()

    return render_template('index.html', battery_data=query1_output)



# New route to handle form submission
@app.route('/submit_form', methods=['POST'])
def submit_form():
    if request.method == 'POST':
        form_data = request.form

        # Extract form data
        discharge = form_data['Discharge']
        decrement = form_data['Decrement']
        mvd = form_data['MVD']
        mvc = form_data['MVC']
        time = form_data['Time']
        tcc = form_data['TCC']
        charging = form_data['Charging']
        rul = form_data['RUL']

        # Insert form data into the database
        connection = get_mysql_connection()
        cursor = connection.cursor()
        
        # Adjust the SQL query based on your table structure
        query = "INSERT INTO battery_rul (discharge, decrement, mvd, mvc, time, tcc, ct, rul) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        values = (discharge, decrement, mvd, mvc, time, tcc, charging, rul)

        cursor.execute(query, values)
        connection.commit()
        cursor.close()

        return redirect(url_for('index'))  # Redirect to the form after submission
    
@app.route('/get_record/<int:record_id>', methods=['GET'])
def get_record(record_id):
    cursor = get_mysql_connection().cursor(dictionary=True)
    query = "SELECT * FROM battery_rul WHERE id = %s"
    cursor.execute(query, (record_id,))
    record_data = cursor.fetchone()
    cursor.close()
    return jsonify(record_data)

# New route to handle updating a record
@app.route('/update_record/<int:record_id>', methods=['POST'])
def update_record(record_id):
    if request.method == 'POST':
        form_data = request.form

        # Extract form data
        discharge = form_data['Discharge']
        decrement = form_data['Decrement']
        mvd = form_data['MVD']
        mvc = form_data['MVC']
        time = form_data['Time']
        tcc = form_data['TCC']
        charging = form_data['Charging']
        rul = form_data['RUL']

        # Update the record in the database
        connection = get_mysql_connection()
        cursor = connection.cursor()

        # Adjust the SQL query based on your table structure
        query = "UPDATE battery_rul SET discharge=%s, decrement=%s, mvd=%s, mvc=%s, time=%s, tcc=%s, ct=%s, rul=%s WHERE id=%s"
        values = (discharge, decrement, mvd, mvc, time, tcc, charging, rul, record_id)

        cursor.execute(query, values)
        connection.commit()
        cursor.close()

        return jsonify({"message": "Record updated successfully"})


if __name__ == '__main__':
    app.run(debug=True)
