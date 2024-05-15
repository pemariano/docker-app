from flask import Flask, render_template

app = Flask(__name__)

# Define a route for the home page
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)

