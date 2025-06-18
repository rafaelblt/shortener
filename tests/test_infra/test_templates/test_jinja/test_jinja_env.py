from shortener.infra.settings import settings
from shortener.infra.templates.jinja.environment import (
    get_jinja_env, get_default_context
)

from jinja2 import Environment, FileSystemLoader


def test_instance():
    retrieved = get_jinja_env(translator=None)
    assert isinstance(retrieved, Environment)
    assert isinstance(retrieved.loader, FileSystemLoader)


def test_jinja_env_default_translator():
    jinja_env = get_jinja_env(translator=None)
    translator = jinja_env.globals["_"]
    text = "This is a test text for tests..."
    assert translator(text) == text


def test_get_default_context():
    assert get_default_context() == {"app_name": settings.APP_NAME}


def test_Jinja_env_default_context():
    jinja_env = get_jinja_env(translator=None)
    default_ctx = get_default_context()
    for key, value in default_ctx.items():
        assert key in jinja_env.globals
        assert jinja_env.globals[key] == value
