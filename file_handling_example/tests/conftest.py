import pytest

from file_handling_example.main import Manager, ProcessorStub, FolderStub

@pytest.fixture
def manager():
    return Manager(processor=ProcessorStub(), folder=FolderStub())
