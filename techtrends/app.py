import sqlite3

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort
from datetime import datetime
import logging
import sys


# Store the total amount of connections to the database
db_connection_count = 0

stdout_handler = logging.StreamHandler(sys.stdout)
stderr_handler = logging.StreamHandler(sys.stderr)
handlers = [stdout_handler, stderr_handler]
logging.basicConfig(handlers=handlers, level=logging.DEBUG)

# Get the current formated date time
def get_current_date_time():
    current = datetime.now()
    return current.strftime("%d/%m/%Y, %H:%M:%S")

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    global db_connection_count
    db_connection_count += 1
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
      app.logger.error("{}, A non-existing article is accessed and a 404 page is returned".format(get_current_date_time()))
      return render_template('404.html'), 404
    else:
      app.logger.debug("{}, Artical \"{}\" retrieved!".format(get_current_date_time(), post['title']))
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    app.logger.debug("{}, The \"About US\" page is retrieved".format(get_current_date_time()))
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
	    app.logger.error("{}, Title is required!".format(get_current_date_time()))
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()
            app.logger.debug("{}, Artical \"{}\" created!".format(get_current_date_time(), title))
            return redirect(url_for('index'))

    return render_template('create.html')

# Define the endpoint to check if the system is up and running
@app.route('/healthz')
def check_healthz():
    try: 
        connection = get_db_connection()
        connection.execute("SELECT ACK as status;")
        connection.commit()
        connection.close()
        return jsonify({"result": "OK - healthy"})
    except:
        return jsonify({"resutl": "ERROR - unhealthy"})

# Define metrics route to display the metrics information about the appliction
@app.route('/metrics')
def get_metrics():
    response = {}
    connection = get_db_connection()
    response['db_connection_count'] = db_connection_count;
    response['post_count'] = connection.execute('SELECT COUNT(*) FROM posts').fetchone()[0]
    connection.commit()
    connection.close()
    return jsonify(response) 


# start the application on port 3111
if __name__ == "__main__":
   app.run(host='0.0.0.0', port='3111')
