import time
from dataclasses import dataclass

import pytchat


@dataclass
class StreamChat:
    _stream: None
    _name: str
    _translation_required: bool
    _connected: bool

    def __init__(self, link: str, name: str, translation_required: bool = False):
        self._name = name
        self._stream = pytchat.create(link, topchat_only=True)
        self._translation_required = translation_required
        self._connected = False
        try:
            self.stream.raise_for_status()
            self._connected = True
        except Exception as e:
            print(type(e), str(e))
        # connection_thread = threading.Thread(target=self.connection_checker)
        # connection_thread.start()

    def __repr__(self):
        return f'Name: {self._name}\n' \
               f'Translation: {"ON" if self.translation_on else "OFF"}\n' \
               f'Status: {"CONNECTED" if self.is_connected() else "DISCONNECTED"}'

    @property
    def stream(self):
        return self._stream

    @property
    def translation_on(self):
        return self._translation_required

    def is_connected(self):
        while 42:
            time.sleep(1)
            try:
                self.stream.raise_for_status()
                self._connected = True
                return True
            except pytchat.ChatDataFinished:
                print("> Chat Data Finished")
                self._connected = False
                return False
            except Exception as e:
                print(type(e), str(e))
                self._connected = False
                return False
