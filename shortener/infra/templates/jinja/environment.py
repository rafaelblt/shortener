import os

from jinja2 import Environment, FileSystemLoader, select_autoescape

from shortener.infra.translations.i18n import default_translator
from shortener.infra.settings import settings


class JinjaEnvironment:
    TEMPLATES_DIR = os.path.dirname(__file__)
    DEFAULT_CONTEXT = {
        "app_name": settings.app_name
    }

    def __init__(self):
        jinja_env = Environment(
            loader=FileSystemLoader(self.TEMPLATES_DIR),
            autoescape=select_autoescape(['html'])
        )
        jinja_env.globals.update(self.DEFAULT_CONTEXT)
        jinja_env.globals["_"] = default_translator
        self._env = jinja_env
    
    def get_template(self, path: str):
        return self._env.get_template(path)
