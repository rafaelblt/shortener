import secrets

from shortener.domain.services.token import RandomTokenGenerator


class URLSafeTokenGenerator(RandomTokenGenerator):
    def generate_token(self) -> str:
        return secrets.token_urlsafe(64)
