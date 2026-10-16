import socket

from collections.abc import Iterator

import pytest


@pytest.fixture
def silent_server() -> Iterator[str]:
    """
    The address, as host:port, of a server that accepts connections and never
    answers them, so whoever connects to it waits until a timeout runs out.
    """
    with socket.create_server(("127.0.0.1", 0)) as server:
        host, port = server.getsockname()
        yield f"{host}:{port}"
