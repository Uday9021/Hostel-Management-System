"""Small browser-based room dashboard for the Hostel Management project."""

from flask import Flask, current_app, jsonify, render_template, request


DEFAULT_ROOMS = [
    {"id": 1, "name": "A-101", "capacity": 4, "occupied": 3},
    {"id": 2, "name": "B-202", "capacity": 2, "occupied": 1},
    {"id": 3, "name": "C-303", "capacity": 3, "occupied": 3},
]


def create_app(initial_rooms=None):
    app = Flask(__name__)
    source_rooms = DEFAULT_ROOMS if initial_rooms is None else initial_rooms
    app.config["ROOMS"] = [dict(room) for room in source_rooms]

    @app.get("/")
    def dashboard():
        return render_template("index.html")

    @app.get("/health")
    def health():
        return jsonify(status="ok")

    @app.get("/api/rooms")
    def list_rooms():
        rooms = current_app.config["ROOMS"]
        capacity = sum(room["capacity"] for room in rooms)
        occupied = sum(room["occupied"] for room in rooms)
        return jsonify(
            rooms=rooms,
            summary={
                "room_count": len(rooms),
                "capacity": capacity,
                "occupied": occupied,
                "available": capacity - occupied,
            },
        )

    @app.post("/api/rooms")
    def add_room():
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return jsonify(error="Send room details as JSON."), 400

        name = payload.get("name")
        capacity = payload.get("capacity")
        occupied = payload.get("occupied", 0)

        if not isinstance(name, str) or not name.strip() or len(name.strip()) > 40:
            return jsonify(error="Room name must contain 1 to 40 characters."), 400
        if isinstance(capacity, bool) or not isinstance(capacity, int) or not 1 <= capacity <= 50:
            return jsonify(error="Capacity must be a whole number from 1 to 50."), 400
        if isinstance(occupied, bool) or not isinstance(occupied, int) or not 0 <= occupied <= capacity:
            return jsonify(error="Occupied beds must be a whole number between 0 and capacity."), 400

        rooms = current_app.config["ROOMS"]
        clean_name = name.strip()
        if any(room["name"].casefold() == clean_name.casefold() for room in rooms):
            return jsonify(error="A room with that name already exists."), 409

        room = {
            "id": max((item["id"] for item in rooms), default=0) + 1,
            "name": clean_name,
            "capacity": capacity,
            "occupied": occupied,
        }
        rooms.append(room)
        return jsonify(room=room), 201

    return app


app = create_app()
