import os

os.environ.setdefault("SENDGRID_API_KEY", "fake-sendgrid-key")
os.environ.setdefault("SENDGRID_FROM_EMAIL", "admin@gmail.com")

from tests.fixtures import *
