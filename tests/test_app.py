import os
import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path
from unittest.mock import patch

from app import create_app, execute_many


class WebsiteTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database_path = Path(self.temp_dir.name) / "test.db"
        self.app = create_app(
            {
                "TESTING": True,
                "DATABASE": str(self.database_path),
            }
        )
        self.client = self.app.test_client()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_homepage_renders_catalog_hours_contacts_and_instagram_gallery(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Jasne", response.data)
        self.assertIn(b"Wile\xc5\x84ska IPA", response.data)
        self.assertIn(b"/beer-label.webp", response.data)
        self.assertIn("Понеділок".encode(), response.data)
        self.assertIn("15:00 – 22:00".encode(), response.data)
        self.assertIn("Неділя".encode(), response.data)
        self.assertIn("13:00 – 04:00".encode(), response.data)
        self.assertIn("ul. Święty Marcin 32, Poznań".encode(), response.data)
        self.assertIn(
            b"query=Castacraftowe+%C5%9Awi%C4%99ty+Marcin+32+Pozna%C5%84",
            response.data,
        )
        self.assertIn(b"tel:+48797356568", response.data)
        self.assertIn(b"https://www.instagram.com/castacraftowe/", response.data)
        self.assertIn(b"/reel/De-FpWzN8al/", response.data)
        self.assertIn(b"/p/De4JHgVtnHP/", response.data)

        image_response = self.client.get("/beer-label.webp")
        self.assertEqual(image_response.status_code, 200)
        image_response.close()

    def test_contact_form_saves_message(self):
        response = self.client.post(
            "/contact",
            data={
                "name": "Danylo",
                "contact": "danylo@example.com",
                "message": "Please reserve a table.",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Ваше повідомлення збережено".encode(), response.data)
        with closing(sqlite3.connect(self.database_path)) as connection:
            row = connection.execute(
                "SELECT name, contact, message FROM contact_messages"
            ).fetchone()
        self.assertEqual(
            row,
            ("Danylo", "danylo@example.com", "Please reserve a table."),
        )

    def test_invalid_contact_form_is_not_saved(self):
        response = self.client.post(
            "/contact",
            data={"name": "Danylo", "contact": "danylo@example.com"},
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("Вкажіть повідомлення".encode(), response.data)
        with closing(sqlite3.connect(self.database_path)) as connection:
            count = connection.execute(
                "SELECT COUNT(*) FROM contact_messages"
            ).fetchone()[0]
        self.assertEqual(count, 0)

    def test_health_check_verifies_database_connection(self):
        response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"status": "ok"})

    def test_vercel_requires_persistent_database(self):
        with patch.dict(os.environ, {"VERCEL": "1", "DATABASE_URL": ""}):
            with self.assertRaisesRegex(RuntimeError, "persistent PostgreSQL"):
                create_app({"TESTING": True, "DATABASE": ":memory:"})

    def test_postgres_batch_insert_uses_cursor_executemany(self):
        class FakeCursor:
            def executemany(self, query, parameters):
                self.query = query
                self.parameters = list(parameters)

            def close(self):
                self.closed = True

        class FakeConnection:
            def cursor(self):
                self.created_cursor = FakeCursor()
                return self.created_cursor

        connection = FakeConnection()
        with self.app.app_context():
            self.app.config["DATABASE_URL"] = "postgresql://test"
            execute_many(connection, "INSERT INTO test VALUES (?)", [(1,), (2,)])

        self.assertEqual(
            connection.created_cursor.query, "INSERT INTO test VALUES (%s)"
        )
        self.assertEqual(connection.created_cursor.parameters, [(1,), (2,)])
        self.assertTrue(connection.created_cursor.closed)


if __name__ == "__main__":
    unittest.main()
