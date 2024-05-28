from flask import Flask, render_template
import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import errorcode
import boto3

load_dotenv()

app = Flask(__name__)





# Database connection variables
host = '...'
username = '...'
password = '...'
database_name = '...'
port = '...'

# Function to get the RDS parameters from SSM.
def getParameter(param_name):
    """
    This function reads a secure parameter from AWS' SSM service.
    The request must be passed a valid parameter name, as well as 
    temporary credentials which can be used to access the parameter.
    The parameter's value is returned.
    """
    # Create the SSM Client
    ssm = boto3.client('ssm',
        region_name='us-east-2'
    )

    # Get the requested parameter
    response = ssm.get_parameters(
        Names=[
            param_name,
        ],
        WithDecryption=True
    )
    
    # Store the credentials in a variable
    credentials = response['Parameters'][0]['Value']

    return credentials

host = getParameter('/Dev/RDS/MySQL/database_host')
username = getParameter('/Dev/RDS/MySQL/database_username')
password = getParameter('/Dev/RDS/MySQL/database_password')
database_name = getParameter('/Dev/RDS/MySQL/database_name')
port = getParameter('/Dev/RDS/MySQL/database_port')





# Function to get data from the RDS database
def get_db_data():
    try:
        connection = mysql.connector.connect(
            host=host,
            user=username,
            password=password,
            database=database_name,
            port=port
        )
        
        if connection.is_connected():
            print("Connection successful!")
        
        cursor = connection.cursor()
        
        cursor.execute("""
            SELECT timestamp, wind_strength, wind_angle, swell_strength, swell_angle, swell_period, rain, temperature
            FROM surf_forecast
            ORDER BY timestamp
            LIMIT 24
        """)
        rows = cursor.fetchall()
        
        # Prepare data for pivoted table
        data = {
            "timestamps": [row[0] for row in rows],
            "wind_strength": [row[1] for row in rows],
            "wind_direction": [row[2] for row in rows],
            "swell_strength": [row[3] for row in rows],
            "swell_direction": [row[4] for row in rows],
            "swell_period": [row[5] for row in rows],
            "rain": [row[6] for row in rows],
            "temperature": [row[7] for row in rows]
        }
        
        cursor.close()
        connection.close()
        return data

    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist.")
        elif err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Username or password is incorrect.")
        else:
            print(err)
        return 'Error in get_db_data'





# Define a route for the home page
@app.route('/')
def index():
    data = get_db_data()
    print(data)
    return render_template('index.html', data=data)

if __name__ == '__main__':
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)

