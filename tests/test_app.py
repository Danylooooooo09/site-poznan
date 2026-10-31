import os
import smtplib
import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path
from unittest.mock import patch

from app import create_app, execute_query


class WebsiteTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database_path = Path(self.temp_dir.name) / "test.db"
        self.app = create_app(
            {
                "TESTING": True,
                "DATABASE": str(self.database_path),
                "DATABASE_URL": "",
            }
        )
        self.client = self.app.test_client()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_homepage_renders_new_service_marketplace(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Spplot", response.data)
        self.assertNotIn(b"Splot", response.data)
        self.assertIn("Dobry fachowiec".encode(), response.data)
        self.assertIn("Hydraulik".encode(), response.data)
        self.assertIn(b"https://wa.me/48572394937", response.data)
        self.assertIn(b"https://t.me/+48572394937", response.data)
        self.assertNotIn(b"Castacraftowe", response.data)
        self.assertNotIn(b"Jasne", response.data)

    def test_removed_brewery_pages_and_assets_are_not_served(self):
        self.assertEqual(self.client.get("/index").status_code, 404)
        self.assertEqual(self.client.get("/beer-label.webp").status_code, 404)

    def test_services_page_lists_local_home_services(self):
        response = self.client.get("/services?lang=pl")

        self.assertEqual(response.status_code, 200)
        for service_name in (
            "Remont i wykończenie",
            "Hydraulik",
            "Elektryk",
            "Sprzątanie",
            "Przeprowadzki",
            "Meble i montaż",
            "Ogród",
        ):
            self.assertIn(service_name.encode(), response.data)

    def test_all_pages_render_in_ukrainian_and_english(self):
        expected_by_language = {
            "uk": {
                "/": "Добрий майстер",
                "/services": "КАТАЛОГ ПОСЛУГ",
                "/request": "Розкажіть, що сталося",
            },
            "en": {
                "/": "A good pro",
                "/services": "SERVICE DIRECTORY",
                "/request": "Tell us what you need",
            },
        }
        for lang, pages in expected_by_language.items():
            for path, expected_text in pages.items():
                with self.subTest(lang=lang, path=path):
                    response = self.client.get(f"{path}?lang={lang}")
                    self.assertEqual(response.status_code, 200)
                    self.assertIn(expected_text.encode(), response.data)

    def test_request_form_preselects_category_and_saves_submission(self):
        form_response = self.client.get("/request?lang=uk&category=plumbing")
        self.assertEqual(form_response.status_code, 200)
        self.assertIn(b'<option value="plumbing" selected>', form_response.data)
        self.assertIn(b"/request?lang=en&amp;category=plumbing", form_response.data)

        response = self.client.post(
            "/request?lang=uk",
            data={
                "lang": "uk",
                "category": "plumbing",
                "location": "Jeżyce, Poznań",
                "details": "Przecieka kran w kuchni.",
                "name": "Danylo",
                "contact": "danylo@example.com",
                "consent": "yes",
            },
        )

        self.assertEqual(response.status_code, 303)
        success_response = self.client.get(response.headers["Location"])
        self.assertEqual(success_response.status_code, 200)
        self.assertIn("ваш запит збережено".encode(), success_response.data)
        self.assertIn("ще не налаштовані".encode(), success_response.data)
        self.client.get(response.headers["Location"])
        with closing(sqlite3.connect(self.database_path)) as connection:
            row = connection.execute(
                """
                SELECT category, location, details, name, contact
                FROM service_requests
                """
            ).fetchone()
        self.assertEqual(
            row,
            (
                "plumbing",
                "Jeżyce, Poznań",
                "Przecieka kran w kuchni.",
                "Danylo",
                "danylo@example.com",
            ),
        )
        with closing(sqlite3.connect(self.database_path)) as connection:
            count = connection.execute(
                "SELECT COUNT(*) FROM service_requests"
            ).fetchone()[0]
        self.assertEqual(count, 1)

    def test_request_sends_email_when_smtp_is_configured(self):
        self.app.config.update(
            SMTP_USERNAME="owner@example.com",
            SMTP_PASSWORD="app-password",
            MAIL_TO="danildyad@gmail.com",
        )
        with patch("app.smtplib.SMTP_SSL") as smtp:
            response = self.client.post(
                "/request?lang=en",
                data={
                    "category": "plumbing",
                    "location": "Jeżyce, Poznań",
                    "details": "Leaking kitchen tap.",
                    "name": "Danylo",
                    "contact": "+48 572 394 937",
                    "consent": "yes",
                },
            )

        self.assertEqual(response.status_code, 303)
        self.assertIn("email=sent", response.headers["Location"])
        smtp.assert_called_once()
        smtp.return_value.__enter__.return_value.login.assert_called_once_with(
            "owner@example.com", "app-password"
        )
        email = smtp.return_value.__enter__.return_value.send_message.call_args.args[0]
        self.assertEqual(email["To"], "danildyad@gmail.com")
        self.assertIn("Danylo", email.get_content())
        success_response = self.client.get(response.headers["Location"])
        self.assertIn("was sent to the site owner".encode(), success_response.data)

    def test_smtp_failure_is_reported_without_losing_saved_request(self):
        self.app.config.update(
            SMTP_USERNAME="owner@example.com",
            SMTP_PASSWORD="invalid-password",
        )
        with patch(
            "app.smtplib.SMTP_SSL",
            side_effect=smtplib.SMTPAuthenticationError(535, b"Authentication failed"),
        ):
            response = self.client.post(
                "/request?lang=en",
                data={
                    "category": "plumbing",
                    "location": "Poznań",
                    "details": "Leaking tap.",
                    "name": "Danylo",
                    "contact": "danylo@example.com",
                    "consent": "yes",
                },
            )

        self.assertEqual(response.status_code, 303)
        self.assertIn("email=failed", response.headers["Location"])
        failure_response = self.client.get(response.headers["Location"])
        self.assertIn("could not be sent".encode(), failure_response.data)
        with closing(sqlite3.connect(self.database_path)) as connection:
            count = connection.execute(
                "SELECT COUNT(*) FROM service_requests"
            ).fetchone()[0]
        self.assertEqual(count, 1)

    def test_invalid_request_is_rejected_and_not_saved(self):
        response = self.client.post(
            "/request",
            data={
                "category": "not-a-service",
                "location": "Poznań",
                "details": "Need a repair.",
                "name": "Danylo",
                "contact": "danylo@example.com",
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("Sprawdź formularz".encode(), response.data)
        with closing(sqlite3.connect(self.database_path)) as connection:
            count = connection.execute(
                "SELECT COUNT(*) FROM service_requests"
            ).fetchone()[0]
        self.assertEqual(count, 0)

    def test_request_requires_explicit_consent(self):
        response = self.client.post(
            "/request",
            data={
                "category": "plumbing",
                "location": "Poznań",
                "details": "Need a repair.",
                "name": "Danylo",
                "contact": "danylo@example.com",
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn(b'name="consent" type="checkbox" value="yes" required', response.data)
        with closing(sqlite3.connect(self.database_path)) as connection:
            count = connection.execute(
                "SELECT COUNT(*) FROM service_requests"
            ).fetchone()[0]
        self.assertEqual(count, 0)

    def test_request_preserves_consent_when_other_validation_fails(self):
        response = self.client.post(
            "/request",
            data={
                "category": "plumbing",
                "location": "Poznań",
                "details": "Need a repair.",
                "contact": "danylo@example.com",
                "consent": "yes",
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn(b'value="yes" required checked', response.data)

    def test_health_check_verifies_database_connection(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"status": "ok"})

    def test_vercel_requires_persistent_database(self):
        with patch.dict(os.environ, {"VERCEL": "1", "DATABASE_URL": ""}):
            with self.assertRaisesRegex(RuntimeError, "persistent PostgreSQL"):
                create_app(
                    {
                        "TESTING": True,
                        "DATABASE": ":memory:",
                        "DATABASE_URL": "",
                    }
                )

    def test_query_uses_postgres_placeholders_when_configured(self):
        class FakeConnection:
            def execute(self, query, parameters):
                self.query = query
                self.parameters = parameters
                return self

        connection = FakeConnection()
        with self.app.app_context():
            self.app.config["DATABASE_URL"] = "postgresql://test"
            execute_query(connection, "SELECT ? AS value", (1,))

        self.assertEqual(connection.query, "SELECT %s AS value")
        self.assertEqual(connection.parameters, (1,))

    def test_initialization_preserves_existing_legacy_tables(self):
        with closing(sqlite3.connect(self.database_path)) as connection:
            connection.executescript(
                """
                CREATE TABLE beers (name TEXT NOT NULL);
                CREATE TABLE contact_messages (name TEXT NOT NULL);
                INSERT INTO beers (name) VALUES ('old catalog record');
                INSERT INTO contact_messages (name) VALUES ('old contact record');
                """
            )

        create_app(
            {
                "TESTING": True,
                "DATABASE": str(self.database_path),
                "DATABASE_URL": "",
            }
        )

        with closing(sqlite3.connect(self.database_path)) as connection:
            self.assertEqual(
                connection.execute("SELECT name FROM beers").fetchone()[0],
                "old catalog record",
            )
            self.assertEqual(
                connection.execute("SELECT name FROM contact_messages").fetchone()[0],
                "old contact record",
            )
            self.assertIsNotNone(
                connection.execute(
                    "SELECT name FROM sqlite_master WHERE name='service_requests'"
                ).fetchone()
            )


if __name__ == "__main__":
    unittest.main()
