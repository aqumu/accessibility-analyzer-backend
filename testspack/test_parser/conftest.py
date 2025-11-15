import pytest
import http.server
import socketserver
import threading
import os
import socket
from contextlib import closing


# Находим свободный порт
def find_free_port():
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]


@pytest.fixture(scope="session")
def local_server():
    """Фикстура для запуска локального HTTP-сервера в отдельном потоке."""

    # Убедимся, что сервер будет раздавать файл test_page.html из текущей папки
    web_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(web_dir)

    port = find_free_port()
    Handler = http.server.SimpleHTTPRequestHandler

    server_address = ("localhost", port)
    httpd = socketserver.TCPServer(server_address, Handler)

    print(f"\nЗапуск локального сервера на http://localhost:{port}...")

    server_thread = threading.Thread(target=httpd.serve_forever)
    server_thread.daemon = True  # Позволяет pytest завершить поток
    server_thread.start()

    base_url = f"http://localhost:{port}"

    # 'yield' передает управление тестам
    yield base_url

    # Код после 'yield' выполняется после завершения всех тестов
    print(f"\nОстановка локального сервера...")
    httpd.shutdown()
    httpd.server_close()
    server_thread.join(timeout=2)