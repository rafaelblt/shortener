import os

from typing import Callable, Optional
from jinja2 import Environment, FileSystemLoader, select_autoescape

from shortener.infra.settings import settings


GettextFunc = Callable[[str], str]


def get_default_context() -> dict[str, str]:
    return {
        "app_name": settings.APP_NAME
    }


def get_jinja_env(translator: Optional[GettextFunc]) -> Environment:
    templates_dir = os.path.dirname(__file__)

    jinja_env = Environment(
        loader=FileSystemLoader(templates_dir),
        autoescape=select_autoescape(['html'])
    )

    if translator:
        jinja_env.globals["_"] = translator
    else:
        jinja_env.globals["_"] = lambda s: s

    jinja_env.globals.update(get_default_context())

    return jinja_env
