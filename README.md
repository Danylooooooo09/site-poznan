# Castacraftowe

Flask site with a SQLite-backed beer catalog and contact form.

## Run locally

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 app.py
```

Open <http://127.0.0.1:5000>. On first run, the app creates
`instance/site.db` and seeds the beer catalog. Contact form submissions are
saved in the same database. Set `DATABASE_PATH` to use a different SQLite file.

Run tests with `python3 -m unittest discover -s tests`.

## Deploy to Vercel

Import `Danylooooooo09/site-poznan` as a Vercel project. Vercel detects the Flask
app in `app.py` automatically and serves files in `public/` from its CDN.

Before deploying, create a PostgreSQL database using a Vercel Marketplace
integration such as Neon, then add its connection string as the `DATABASE_URL`
environment variable for Production and Preview. Vercel's function filesystem
is ephemeral, so SQLite is intentionally rejected in the Vercel environment.
The app creates the tables and seeds the beer catalog on its first start.

The `origin` GitHub remote is already configured. Commit and push changes to
trigger a Vercel deployment after importing the repository.