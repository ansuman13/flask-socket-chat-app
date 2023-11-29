from flask import Flask, render_template, request, session, redirect, url_for

from flask_socketio import join_room, leave_room, send, SocketIO

import random

from string import ascii_uppercase

app = Flask(__name__)
app.config["SECRET_KEY"] = "abcdefghijklmnopqrstuvwxyz"
socketio  = SocketIO(app)

rooms = {}

def generate_unique_code(char_len):
    while True:
        code = ""
        for _ in range(char_len):
            code += random.choice(ascii_uppercase)

        if code not in rooms:
            break
    
    return code

@app.route('/', methods=["POST", "GET"])
def home():
    session.clear()
    if request.method == "POST":
        name = request.form.get("name")
        code = request.form.get("code")
        join = request.form.get("join", False)
        create = request.form.get("create", False)

        # join = False
        # create = False

        print(request.form)
        if 'create' in request.form:
            create = True
        if 'join' in request.form:
            join = True
            
        if not name:
            return render_template("home.html", error="Error! No Name Specified", code=code, name=name)
        
        if join and not code:
            return render_template("home.html", error="No Code Specified", code=code, name=name)
        
        room = code
        if create:
            room = generate_unique_code(4)
            rooms[room] = {'members': 0 , "messages": []}

        elif code not in rooms:
            return render_template("home.html", error="Room Does not exist", code=code, name=name)

        session["room"] = room
        session["name"] = name
        return redirect(url_for("room"))

    return render_template("home.html")

@app.route("/room")
def room():
    room = session.get("room")
    if room is None or session.get("name") is None or room not in rooms:
        return redirect(url_for("home"))

    return render_template("room.html", room=room)

@socketio.on("connect")
def connect():
    room = session.get("room")
    name = session.get("name")
    join_room(room)
    send({"name": name, "message": "has joined the room"}, to=room)
    rooms[room]["members"] += 1
    print(f"user {name} joined the Room {room}")
    
@socketio.on("disconnect")
def disconnect():
    room = session.get("room")
    name = session.get("name")
    leave_room(room)
    
    send({"name": name, "message": "has left the room"}, to=room)
    rooms[room]["members"] += 1
    print(f"user {name} left the Room {room}") 

@socketio.on("message")
def message(data):
    room = session.get("room")
    name = session.get("name")
    print(data)
    socketio.send({"name": name, "message": data}, to=room)

if __name__ == "__main__":
    socketio.run(app,debug=True, port=8000)
