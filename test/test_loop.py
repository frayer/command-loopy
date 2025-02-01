from dataclasses import dataclass
from typing import Any

import pytest

from command_loopy import command, loop


@dataclass
class CounterUpdatedMsg:
    """
    A test event message indicating that the counter has been updated.
    This is not the class under test but supports the test.
    """

    updated_count: int


class IncrementCounterCmd:
    """
    A test command that increments a counter.
    This is not the class under test but supports the test.
    """

    def __init__(self, current: int = 0):
        self.current = current

    async def exec(self):
        return CounterUpdatedMsg(self.current + 1)


class MockModel:
    """
    A mock model that keeps track of a counter.
    This is not the class under test but supports the test.
    """

    def __init__(self, max_count: int):
        self.max_count = max_count
        self.count = 0
        self.display: str = ""

    def init(self):
        return IncrementCounterCmd()

    def update(self, msg: Any):
        if isinstance(msg, CounterUpdatedMsg):
            self.count += msg.updated_count

        if self.count < self.max_count:
            return (self, IncrementCounterCmd())
        else:
            return (self, command.Quit())

    def view(self):
        self.display = f"count: {self.count}"


@pytest.fixture
def loop_fixture():
    return loop.Loop(command.NoOp(), 0)


@pytest.mark.asyncio
async def test_loop_model(loop_fixture: loop.Loop):
    COUNT = 5
    mdl = MockModel(max_count=COUNT)
    await loop_fixture.run(mdl)
    assert mdl.count == COUNT


@pytest.mark.asyncio
async def test_loop_view(loop_fixture: loop.Loop):
    COUNT = 5
    mdl = MockModel(max_count=COUNT)
    await loop_fixture.run(mdl)
    assert mdl.display == f"count: {COUNT}"
