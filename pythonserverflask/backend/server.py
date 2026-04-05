from flask import Flask, render_template
from markupsafe import escape

app = Flask(__name__)

# Define routes for the application 
# sand an HTML pages to the user when they visit the website

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/greet/<name>')
def greet(name):
    return render_template('greet.html', name=name)

if __name__ == '__main__':
    app.run(debug=True)
