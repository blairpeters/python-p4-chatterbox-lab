from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from models import db, Message
from datetime import datetime

# Initialize the Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

# Enable CORS
CORS(app)

# Initialize database and migrations
db.init_app(app)
migrate = Migrate(app, db)

# Routes

# GET /messages: Fetch all messages ordered by created_at in ascending order
@app.route('/messages', methods=['GET', 'POST'])
def messages():
    if request.method == "GET":
        # Fetch messages ordered by 'created_at'
        messages = Message.query.order_by(Message.created_at.asc()).all()
        response = [message.to_dict() for message in messages]
        return make_response(jsonify(response), 200)

    elif request.method == "POST":
        data = request.get_json()
        if not data or 'body' not in data or 'username' not in data:
            return jsonify({"error": "Missing 'body' or 'username'"}), 400

        # Create a new message
        new_message = Message(
            body=data['body'],
            username=data['username'],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.session.add(new_message)
        db.session.commit()

        return make_response(jsonify(new_message.to_dict()), 201)

# GET, PATCH, DELETE /messages/<int:id>: Fetch, update, or delete a message by ID
@app.route('/messages/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
def messages_by_id(id):
    # Use the recommended Session.get() method
    message = db.session.get(Message, id)

    if message is None:
        return make_response({"error": "Message not found"}, 404)

    if request.method == "GET":
        return make_response(jsonify(message.to_dict()), 200)

    elif request.method == "PATCH":
        data = request.get_json()
        if 'body' in data:
            message.body = data['body']
            message.updated_at = datetime.utcnow()
        db.session.commit()
        return make_response(jsonify(message.to_dict()), 200)

    elif request.method == "DELETE":
        db.session.delete(message)
        db.session.commit()
        return make_response({"message": "Message deleted"}, 200)

# Run the app
if __name__ == '__main__':
    app.run(port=5555)
