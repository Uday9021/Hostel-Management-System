import unittest

from app import create_app


class HostelDashboardTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app(
            [
                {"id": 1, "name": "A-101", "capacity": 4, "occupied": 3},
                {"id": 2, "name": "B-202", "capacity": 2, "occupied": 1},
            ]
        )
        self.client = self.app.test_client()

    def test_dashboard_loads(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Hostel rooms", response.data)

    def test_health_endpoint_is_ready(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"status": "ok"})

    def test_room_list_includes_capacity_summary(self):
        response = self.client.get("/api/rooms")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json()["summary"],
            {"room_count": 2, "capacity": 6, "occupied": 4, "available": 2},
        )

    def test_room_can_be_added(self):
        response = self.client.post(
            "/api/rooms",
            json={"name": "C-303", "capacity": 3, "occupied": 1},
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json()["room"]["id"], 3)

    def test_room_rejects_occupancy_over_capacity(self):
        response = self.client.post(
            "/api/rooms",
            json={"name": "C-303", "capacity": 2, "occupied": 3},
        )
        self.assertEqual(response.status_code, 400)

    def test_room_names_must_be_unique(self):
        response = self.client.post(
            "/api/rooms",
            json={"name": "a-101", "capacity": 2, "occupied": 0},
        )
        self.assertEqual(response.status_code, 409)


if __name__ == "__main__":
    unittest.main()
