import zmq
import subprocess
import socket
from contextlib import closing


def find_free_port():
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(("", 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]


if __name__ == "__main__":
    messages = [
        "Use example_database;",
        "SELECT * FROM cars WHERE NAME LIKE 'C__';",
    ]
    port = find_free_port()
    conn = subprocess.Popen(["python3", "exceldb/main.py", "-c", str(port)])
    context = zmq.Context()
    socket = context.socket(zmq.PAIR)
    socket.connect(f"tcp://localhost:{port}")
    for i in messages:
        socket.send_json({"statement": i})
        print(socket.recv_json())
        # socket.recv_json()
    conn.terminate()
