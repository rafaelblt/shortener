import os


TEST_ENV_VARS = {
    "API_BASE_URL": "https://testshort.com",
    "DATABASE_URL": "sqlite+aiosqlite:///:memory:",
    "ALEMBIC_DATABASE_URL": "",
    "JWT_AUTH_SECRET_KEY": "[TestShort]->S3cr3tK3y!@#$%&*()-+",
    "SENDGRID_API_KEY": "fake-sendgrid-key",
    "SENDGRID_FROM_EMAIL": "admin@gmail.com"
}

def set_test_env_vars():
    for var, value in TEST_ENV_VARS.items():
        os.environ.setdefault(var, value)
