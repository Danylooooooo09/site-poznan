# Spplot — local services MVP

Spplot is a three-page lead-generation prototype for home services in Poznań and
nearby towns. Its interface is available in Polish, Ukrainian, and English:

- `/` — landing page and introduction
- `/services` — local home-service categories
- `/request` — request form; accepts a service category as `?category=plumbing`

The first release focuses on renovation, plumbing, electrical work, cleaning,
moving, furniture assembly, garden work, and other local jobs. It does not yet
have a provider directory or automatically forward requests to professionals.
The form saves requests in the database and emails a notification to the site
owner when Gmail SMTP is configured. WhatsApp and Telegram contact links are
available throughout the site.
Before accepting real customer data publicly, add and link a privacy notice
covering the data controller, purpose and legal basis, retention period, and
the customer's rights.

## Run locally

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 app.py
```

Open <http://127.0.0.1:5000>. By default, the app creates
`instance/site.db`; set `DATABASE_PATH` to select another SQLite database.
Set `DATABASE_URL` to use PostgreSQL. Existing beer-catalog and contact-message
tables are left untouched; new service requests are written to
`service_requests`.

Run tests with:

```sh
python3 -m unittest discover -s tests -v
```

## Deploy to Vercel

The app is configured for the existing Vercel project connected to this GitHub
repository. Configure a persistent PostgreSQL connection as `DATABASE_URL` in
Vercel Production and Preview environments. Vercel's function filesystem is
ephemeral, so the app rejects SQLite in the Vercel environment.

Pushing a commit to the connected branch triggers a deployment. This MVP does
not distribute requests to service providers. To enable email notifications,
create a Google App Password for the sending Gmail account and configure these
environment variables in Vercel (Production and Preview):

- `SMTP_USERNAME` — Gmail address used to send notifications (defaults to
  `danildyad@gmail.com`)
- `SMTP_PASSWORD` — Google App Password; add this only in Vercel's encrypted
  environment-variable settings, never in source control
- `MAIL_TO` — notification recipient (defaults to `danildyad@gmail.com`)
- `MAIL_FROM` — optional sender address (defaults to `SMTP_USERNAME`)
- `SMTP_HOST` — optional, defaults to `smtp.gmail.com`
- `SMTP_PORT` — optional, defaults to `465` (implicit TLS)

Until `SMTP_PASSWORD` is configured, requests are still stored but the form
explicitly tells the customer that the email notification could not be sent.
The site also provides direct WhatsApp and Telegram links as a fallback.
