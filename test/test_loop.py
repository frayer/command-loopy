from dataclasses import dataclass
from unittest import IsolatedAsyncioTestCase

from command_loopy import command as c, loop


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


class TestModel:
    """
    A test model that keeps track of a counter.
    This is not the class under test but supports the test.
    """

    def __init__(self, max_count: int):
        self.max_count = max_count
        self.count = 0
        self.display: str = ""

    def init(self):
        return IncrementCounterCmd()

    def update(self, msg):
        if isinstance(msg, CounterUpdatedMsg):
            self.count += msg.updated_count

        if self.count < self.max_count:
            return (self, IncrementCounterCmd())
        else:
            return (self, c.Quit())

    def view(self):
        self.display = f"count: {self.count}"


class TestLoop(IsolatedAsyncioTestCase):
    """
    This is the actual test class.
    """

    def setUp(self) -> None:
        self.loop = loop.Loop(c.NoOp(), 0)
        return super().setUp()

    async def test_loop_model(self):
        mdl = TestModel(max_count=5)
        await self.loop.run(mdl)
        self.assertEqual(mdl.count, 5)

    async def test_loop_view(self):
        mdl = TestModel(max_count=5)
        await self.loop.run(mdl)
        self.assertEqual(mdl.display, "count: 5")
