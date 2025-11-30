import pytest

@pytest.fixture(autouse=True)
def no_network(monkeypatch):
	# Prevent tests from making network calls accidentally
	import socket
	monkeypatch.setattr(socket, 'socket', lambda *args, **kwargs: None)
