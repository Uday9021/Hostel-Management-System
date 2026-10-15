"""Browser-based hostel room dashboard with persistent SQLite storage."""

import os
import sqlite3
import uuid
from pathlib import Path

from flask import Flask, current_app, g, jsonify, render_template, request


DEFAULT_ROOMS = [
    {"id": 1, "name": "A-101", "capacity": 4, "occupied": 3},
    {"id": 2, "name": "B-202", "capacity": 2, "occupied": 1},
    {"id": 3, "name": "C-303", "capacity": 3, "occupied": 3},
]


def _connect(path, use_uri):
    connection = sqlite3.connect(path, uri=use_uri, timeout=10)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA busy_timeout = 10000")
    return connection


def _initialize_database(app, initial_rooms):
    database_path = app.config["DATABASE_PATH"]
    use_uri = app.config["DATABASE_URI"]
    if not use_uri:
        Path(database_path).parent.mkdir(parents=True, exist_ok=True)

    connection = _connect(database_path, use_uri)
    try:
        if not use_uri:
            connection.execute("PRAGMA journal_mode = WAL")
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS rooms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL COLLATE NOCASE UNIQUE
                    CHECK (length(trim(name)) BETWEEN 1 AND 40),
                capacity INTEGER NOT NULL CHECK (capacity BETWEEN 1 AND 50),
                occupied INTEGER NOT NULL CHECK (occupied BETWEEN 0 AND capacity)
            );
            CREATE TABLE IF NOT EXISTS app_meta (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );
            """
        )

        seeded = connection.execute(
            "SELECT value FROM app_meta WHERE key = ?", ("rooms_seeded",)
        ).fetchone()
        if seeded is None:
            rooms_to_seed = DEFAULT_ROOMS if initial_rooms is None else initial_rooms
            connection.executemany(
                "INSERT INTO rooms (id, name, capacity, occupied) VALUES (?, ?, ?, ?)",
                [
                    (room["id"], room["name"], room["capacity"], room["occupied"])
                    for room in rooms_to_seed
                ],
            )
            connection.execute(
                "INSERT INTO app_meta (key, value) VALUES (?, ?)",
                ("rooms_seeded", "1"),
            )
        connection.commit()
    finally:
        connection.close()


def _get_db():
    if "database" not in g:
        g.database = _connect(
            current_app.config["DATABASE_PATH"], current_app.config["DATABASE_URI"]
        )
    return g.database


def _room_summary(rooms):
    capacity = sum(room["capacity"] for room in rooms)
    occupied = sum(room["occupied"] for room in rooms)
    return {
        "room_count": len(rooms),
        "capacity": capacity,
        "occupied": occupied,
        "available": capacity - occupied,
    }


def _validated_room(payload):
    if not isinstance(payload, dict):
        return None, "Send room details as JSON."

    name = payload.get("name")
    capacity = payload.get("capacity")
    occupied = payload.get("occupied", 0)

    if not isinstance(name, str) or not name.strip() or len(name.strip()) > 40:
        return None, "Room name must contain 1 to 40 characters."
    if isinstance(capacity, bool) or not isinstance(capacity, int) or not 1 <= capacity <= 50:
        return None, "Capacity must be a whole number from 1 to 50."
    if isinstance(occupied, bool) or not isinstance(occupied, int) or not 0 <= occupied <= capacity:
        return None, "Occupied beds must be a whole number between 0 and capacity."
    return {"name": name.strip(), "capacity": capacity, "occupied": occupied}, None


def create_app(initial_rooms=None, database_path=None):
    app = Flask(__name__)

    if database_path is not None:
        resolved_path = database_path
        use_uri = str(database_path).startswith("file:")
    elif initial_rooms is not None:
        # Each test app receives its own shared in-memory database. The anchor
        # connection keeps it alive between Flask request contexts.
        resolved_path = "file:hostel-{}?mode=memory&cache=shared".format(uuid.uuid4().hex)
        use_uri = True
    else:
        resolved_path = os.environ.get(
            "HOSTEL_DATABASE", str(Path(app.instance_path) / "hostel.db")
        )
        use_uri = str(resolved_path).startswith("file:")

    app.config["DATABASE_PATH"] = str(resolved_path)
    app.config["DATABASE_URI"] = use_uri

    if use_uri and "mode=memory" in str(resolved_path):
        app.extensions["hostel_database_anchor"] = _connect(resolved_path, True)

    _initialize_database(app, initial_rooms)

    @app.teardown_appcontext
    def close_database(_error=None):
        connection = g.pop("database", None)
        if connection is not None:
            connection.close()

    @app.get("/")
    def dashboard():
        return render_template("index.html")

    @app.get("/health")
    def health():
        _get_db().execute("SELECT 1").fetchone()
        return jsonify(status="ok")

    @app.get("/api/rooms")
    def list_rooms():
        rows = _get_db().execute(
            "SELECT id, name, capacity, occupied FROM rooms ORDER BY id"
        ).fetchall()
        rooms = [dict(row) for row in rows]
        return jsonify(rooms=rooms, summary=_room_summary(rooms))

    @app.post("/api/rooms")
    def add_room():
        room, error = _validated_room(request.get_json(silent=True))
        if error:
            return jsonify(error=error), 400

        connection = _get_db()
        try:
            cursor = connection.execute(
                "INSERT INTO rooms (name, capacity, occupied) VALUES (?, ?, ?)",
                (room["name"], room["capacity"], room["occupied"]),
            )
            connection.commit()
        except sqlite3.IntegrityError:
            connection.rollback()
            return jsonify(error="A room with that name already exists."), 409

        room["id"] = cursor.lastrowid
        return jsonify(room=room), 201

    @app.put("/api/rooms/<int:room_id>")
    def update_room(room_id):
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return jsonify(error="Send the occupied bed count as JSON."), 400
        occupied = payload.get("occupied")
        if isinstance(occupied, bool) or not isinstance(occupied, int) or occupied < 0:
            return jsonify(error="Occupied beds must be a non-negative whole number."), 400

        connection = _get_db()
        room = connection.execute(
            "SELECT capacity FROM rooms WHERE id = ?", (room_id,)
        ).fetchone()
        if room is None:
            return jsonify(error="Room not found."), 404
        if occupied > room["capacity"]:
            return jsonify(error="Occupied beds cannot exceed room capacity."), 400

        connection.execute(
            "UPDATE rooms SET occupied = ? WHERE id = ?", (occupied, room_id)
        )
        connection.commit()
        return jsonify(status="updated", id=room_id, occupied=occupied)

    @app.delete("/api/rooms/<int:room_id>")
    def delete_room(room_id):
        connection = _get_db()
        cursor = connection.execute("DELETE FROM rooms WHERE id = ?", (room_id,))
        connection.commit()
        if cursor.rowcount == 0:
            return jsonify(error="Room not found."), 404
        return jsonify(status="deleted", id=room_id)

    return app


app = create_app()
