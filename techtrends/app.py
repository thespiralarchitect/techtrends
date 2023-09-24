import sqlite3

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort
from datetime import datetime
import logging

# Init count of connections
db_connection_count = 0

# Format a message to include timestamp
def message_with_ts(msg):
    return '{timestamp}, {message}'.format(
        timestamp=datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
        message=msg
    )

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    global db_connection_count
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    db_connection_count += 1
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

def get_post_count():
    connection = get_db_connection()
    res = connection.execute('SELECT COUNT(id) AS total FROM posts').fetchone()
    connection.close()
    return res['total']

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
        app.logger.info(message_with_ts('Requested post with ID={post_id} not found.'.format(post_id=post_id)))
        return render_template('404.html'), 404
    else:
        app.logger.info(message_with_ts('Requested post {title} retrieved.'.format(title=post['title'])))
        return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    app.logger.info(message_with_ts('About Us page retrieved.'))
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()

            app.logger.info(message_with_ts('New post {title} retrieved.'.format(title=post['title'])))
            return redirect(url_for('index'))

    return render_template('create.html')

# Define Healthcheck endpoint
@app.route('/healthz')
def healthcheck():
    return jsonify({
        'result': 'OK - healthy'
    })

# Define metrics endpoint
@app.route('/metrics')
def metrics():
    return jsonify({
        'post_count': get_post_count(),
        'db_connection_count': db_connection_count
    })

# start the application on port 3111
if __name__ == "__main__":
    app.logger.setLevel(logging.DEBUG)
    app.run(host='0.0.0.0', port='3111')
