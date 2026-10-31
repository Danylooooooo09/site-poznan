# Splot — local services MVP

Splot is a three-page lead-generation prototype for home services in Poznań and
nearby towns. Its interface is available in Polish, Ukrainian, and English:

- `/` — landing page and introduction
- `/services` — local home-service categories
- `/request` — request form; accepts a service category as `?category=plumbing`

The first release focuses on renovation, plumbing, electrical work, cleaning,
moving, furniture assembly, garden work, and other local jobs. It does not yet
have a provider directory or automatically forward requests to professionals.
The form states this clearly and saves submitted requests in the database.
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
not yet email requests or distribute them to service providers.
