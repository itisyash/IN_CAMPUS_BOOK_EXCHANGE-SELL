from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_socketio import SocketIO, send
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app)

# Database initialization
def init_db():
    if not os.path.exists('database.db'):
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        sender_id INTEGER NOT NULL,
                        receiver_id INTEGER NOT NULL,
                        message TEXT NOT NULL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )''')
        conn.commit()
        conn.close()

# Chat route
@app.route('/chat/<int:receiver_id>')
def chat(receiver_id):
    return render_template('chat.html', receiver_id=receiver_id)

# SocketIO event for handling messages
@socketio.on('message')
def handle_message(data):
    sender_id = data['sender_id']
    receiver_id = data['receiver_id']
    message = data['message']

    # Save message to the database
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('INSERT INTO messages (sender_id, receiver_id, message) VALUES (?, ?, ?)', (sender_id, receiver_id, message))
    conn.commit()
    conn.close()

    # Broadcast the message to the receiver
    send({'sender_id': sender_id, 'message': message}, room=str(receiver_id))

if __name__ == '__main__':
    init_db()
    socketio.run(app, debug=True)
# Homepage
@app.route('/')
def index():
    return render_template('index.html')


# Dashboard
@app.route('/dashboard')
def dashboard():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT * FROM books')
    books = c.fetchall()
    conn.close()
    return render_template('dashboard.html', books=books)

# Add Book Listing
@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        price = request.form['price']
        seller_id = 1  # Default seller ID (you can remove this if not needed)

        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('INSERT INTO books (title, author, price, seller_id) VALUES (?, ?, ?, ?)', (title, author, price, seller_id))
        conn.commit()
        conn.close()

        flash('Book added successfully!')
        return redirect(url_for('dashboard'))
    return render_template('add_book.html')
# Edit Book Listing
@app.route('/edit_book/<int:book_id>', methods=['GET', 'POST'])
def edit_book(book_id):
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        price = request.form['price']

        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('UPDATE books SET title = ?, author = ?, price = ? WHERE id = ?', (title, author, price, book_id))
        conn.commit()
        conn.close()

        flash('Book updated successfully!')
        return redirect(url_for('dashboard'))
    
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT * FROM books WHERE id = ?', (book_id,))
    book = c.fetchone()
    conn.close()
    return render_template('edit_book.html', book=book)

# Delete Book Listing
@app.route('/delete_book/<int:book_id>')
def delete_book(book_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('DELETE FROM books WHERE id = ?', (book_id,))
    conn.commit()
    conn.close()

    flash('Book deleted successfully!')
    return redirect(url_for('dashboard'))

# Real-time Chat
@app.route('/chat/<int:receiver_id>')
def chat(receiver_id):
    return render_template('chat.html', receiver_id=receiver_id)

# SocketIO Event for Real-time Chat
@socketio.on('message')
def handle_message(data):
    sender_id = data['sender_id']
    receiver_id = data['receiver_id']
    message = data['message']

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('INSERT INTO messages (sender_id, receiver_id, message) VALUES (?, ?, ?)', (sender_id, receiver_id, message))
    conn.commit()
    conn.close()

    send({'sender_id': sender_id, 'message': message}, room=str(receiver_id))

if __name__ == '__main__':
    init_db()
    socketio.run(app, debug=True)