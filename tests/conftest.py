import pytest

from main import Manager, ProcessorStub, FolderStub

@pytest.fixture
def manager():
    return Manager(processor=ProcessorStub(), folder=FolderStub())
