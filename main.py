import abc
import asyncio
from io import BufferedIOBase

class Processor(abc.ABC):
    def encrypt_and_compress(self, data: bytes) -> bytes:
        ...

    def decrypt_and_decompress(self, data: bytes) -> bytes:
        ...


class Folder(abc.ABC):
    MAX_FILE_SIZE = 1024 * 1024 * 100
    async def write_file(self, name: str, data: bytes) -> None:
        ...

    async def read_file(self, name: str) -> bytes:
        ...

    async def list_files(self) -> list[str]:
        ...



class Manager:
    def __init__(self, processor: Processor, folder: Folder) -> None:
        self._processor = processor
        self._folder = folder

    async def backup(self, in_stream: BufferedIOBase):
        pass

    async def restore(self, out_stream: BufferedIOBase):
        pass



class FolderStub(Folder):
    MAX_FILE_SIZE = 10
    files = {}
    delay = 0.02

    async def write_file(self, name: str, data: bytes) -> None:
        if len(data) > self.MAX_FILE_SIZE:
            raise ValueError("File too large")
        await asyncio.sleep(self.delay)
        self.files[name] = data

    async def read_file(self, name: str) -> bytes:
        if name not in self.files:
            raise ValueError("File not found")
        await asyncio.sleep(self.delay)
        return self.files[name]

    async def list_files(self) -> list[str]:
        await asyncio.sleep(self.delay)
        return list(self.files.keys())


class ProcessorStub(Processor):
    def __init__(self, encryption_key: int = 0x55):
        self._encryption_key = encryption_key

    def encrypt_and_compress(self, data: bytes) -> bytes:
        if not data:
            return b""
        return bytes(b ^ self._encryption_key for b in data)

    def decrypt_and_decompress(self, data: bytes) -> bytes:
        if not data:
            return b""
        return bytes(b ^ self._encryption_key for b in data)

