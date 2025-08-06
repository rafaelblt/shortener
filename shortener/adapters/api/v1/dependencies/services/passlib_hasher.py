from shortener.infra.services.passlib_hasher import PasslibPasswordHasher


def make_passlib_password_hasher():
    return PasslibPasswordHasher()
