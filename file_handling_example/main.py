import abc
import asyncio
from io import BufferedIOBase, BytesIO
from typing import AsyncGenerator, AsyncIterable


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


async def aenumerate(async_iterable: AsyncIterable):
    idx = 0
    async for item in async_iterable:
        yield idx, item
        idx += 1


class Manager:
    def __init__(self, processor: Processor, folder: Folder) -> None:
        self._processor = processor
        self._folder = folder

    async def backup(self, in_stream: BufferedIOBase):
        chunk_size = self._folder.MAX_FILE_SIZE
        async with asyncio.TaskGroup() as tg:
            async for idx, chunk in aenumerate(self._get_chunks(in_stream, chunk_size)):
                encrypted_chunk = self._processor.encrypt_and_compress(chunk)
                chunk_name = f"{idx}_backup"
                tg.create_task(self._folder.write_file(chunk_name, encrypted_chunk))

    async def restore(self, out_stream: BufferedIOBase):
        files = await self._folder.list_files()

        lock = asyncio.Lock()
        semaphore = asyncio.Semaphore(3)
        async with asyncio.TaskGroup() as tg:
            for i in range(len(files)):
                tg.create_task(self._read_and_decypher(i, out_stream, lock, semaphore))

        out_stream.seek(0)
        return out_stream

    async def _get_chunks(self, in_stream: BufferedIOBase, chunk_size: int) -> AsyncGenerator[bytes]:
        while True:
            data = await asyncio.to_thread(in_stream.read, chunk_size)
            if not data:
                break
            yield data

    async def _read_and_decypher(self, idx, out, lock, semaphore):
        async with semaphore:
            name = f"{idx}_backup"
            chunk = await self._folder.read_file(name)
            decrypted_chunk = self._processor.decrypt_and_decompress(chunk)
            offset = idx * self._folder.MAX_FILE_SIZE
            async with lock:
                out.seek(offset)
                await asyncio.to_thread(out.write, decrypted_chunk)
        return self._processor.decrypt_and_decompress(chunk)


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


async def main():
    manager = Manager(processor=ProcessorStub(), folder=FolderStub())
    await manager.backup(BytesIO(b"This is the text that will be divided into multiple files"))

    out = BytesIO()
    await manager.restore(out)
    print(out.read())


if __name__ == '__main__':
    asyncio.run(main())
