from shortener.infra.settings import settings
from shortener.infra.translations.i18n import default_translator
from shortener.infra.templates.jinja.environment import JinjaEnvironment

from jinja2 import Environment, FileSystemLoader


def test_attr_env_instance():
    env = JinjaEnvironment()._env
    assert isinstance(env, Environment)
    assert isinstance(env.loader, FileSystemLoader)
    assert env.loader.searchpath == [JinjaEnvironment.TEMPLATES_DIR]


def test_env_default_translator():
    env = JinjaEnvironment()._env
    assert env.globals["_"] == default_translator


def test_attr_default_context():
    expected_ctx = {"app_name": settings.APP_NAME}
    assert JinjaEnvironment.DEFAULT_CONTEXT == expected_ctx


def test_default_context_in_jinja_env():
    jinja_env = JinjaEnvironment()._env
    default_ctx = JinjaEnvironment.DEFAULT_CONTEXT
    for key, value in default_ctx.items():
        assert key in jinja_env.globals
        assert jinja_env.globals[key] == value
