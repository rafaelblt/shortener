import os


environment = {
    "API_BASE_URL": "https://testshort.com",
    "DATABASE_URL": "sqlite+aiosqlite:///:memory:",
    "ALEMBIC_DATABASE_URL": "http://false-albemcin.com",
    "JWT_SECRET_KEY": "[TestShort]->S3cr3tK3y!@#$%&*()-+",
    "SENDGRID_API_KEY": "fake-sendgrid-key",
    "SENDGRID_FROM_EMAIL": "admin@gmail.com"
}

for var, value in environment.items():
    os.environ.setdefault(var, value)
