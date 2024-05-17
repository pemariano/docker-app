from flask import Flask, render_template
import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Function to get data from the RDS database
def get_db_data():
    # Connect to your MySQL database on RDS using environment variables
    connection = pymysql.connect(
        host=os.getenv('MYSQL_HOST'),
        database=os.getenv('MYSQL_DATABASE'),
        user=os.getenv('MYSQL_USER'),
        password=os.getenv('MYSQL_PASSWORD'),
        port=os.getenv('MYSQL_PORT')
    )
    cursor = connection.cursor()
    cursor.execute("""
        SELECT timestamp, wind_strength, wind_angle, swell_strength, swell_angle, swell_period, rain, temperature
        FROM surf_forecast
        ORDER BY timestamp
        LIMIT 24
    """)
    data = cursor.fetchall()
    cursor.close()
    connection.close()
    return data


# Define a route for the home page
@app.route('/')
def index():
    data = get_db_data()
    return render_template('index.html', data=data)

if __name__ == '__main__':
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)

