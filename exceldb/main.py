from parser import Parser
from execute import execute
import argparse
import zmq


def connection(port):
    context = zmq.Context()
    socket = context.socket(zmq.PAIR)
    socket.bind(f"tcp://*:{port}")

    while True:
        statement = socket.recv_json()["statement"]

        try:
            tree = Parser(statement)
            result = execute(tree)
            socket.send_json({"type": "result", "value": str(result)})
        except Exception as error:
            socket.send_json({"type": "error", "value": str(error)})


def single(statement):
    pass


def file(path):
    pass


if __name__ == "__main__":
    modes = {"connection": connection, "single": single, "file": file}

    parser = argparse.ArgumentParser(allow_abbrev=False)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-c", "--connection", action="store", type=int, metavar="port")
    group.add_argument("-s", "--single", action="store", metavar="statement")
    group.add_argument("-f", "--file", action="store", metavar="path")
    args = parser.parse_args()

    mode, value = [(x, y) for x, y in vars(args).items() if y != None][0]
    modes[mode](value)
