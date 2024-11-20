from flask import Flask, render_template, jsonify, request
from time import sleep

app = Flask(__name__)

# Simulated database
users = []


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username', '').strip()
    role = data.get('role', '')
    newsletter = data.get('newsletter', False)

    # Validation
    if not username:
        return jsonify({'status': 'error', 'message': 'Username is required'}), 400
    if not role:
        return jsonify({'status': 'error', 'message': 'Role is required'}), 400
    if username in [user['username'] for user in users]:
        return jsonify({'status': 'error', 'message': 'Username already exists'}), 400

    users.append({
        'username': username,
        'role': role,
        'newsletter': newsletter
    })

    return jsonify({'status': 'success', 'message': 'Registration successful'})


@app.route('/api/load-content')
def load_content():
    # Simulate delay
    sleep(1)
    return jsonify({
        'content': 'This content was loaded dynamically!'
    })


if __name__ == '__main__':
    app.run(debug=True)