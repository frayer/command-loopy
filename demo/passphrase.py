import asyncio
from dataclasses import dataclass
from enum import Enum
from typing import Any

from command_loopy import command, loop


class MsgType(Enum):
    INITIAL_PASSPHRASE = "initial_passphrase"
    GET_PASSPHRASE = "get_passphrase"


class TypedStringMsg:
    def __init__(self, msg: str, msg_type: MsgType):
        self.msg = msg
        self.msg_type = msg_type


class GetInputCmd:
    def __init__(self, msg_type: MsgType):
        self.msg_type = msg_type

    async def exec(self):
        p = input()
        return TypedStringMsg(p, self.msg_type)


@dataclass
class ModelState:
    passphrase: str | None
    correct: bool
    attempts: int


class Model:
    def __init__(self):
        self.state: ModelState = ModelState(
            passphrase=None,
            correct=False,
            attempts=0,
        )

    def init(self):
        return GetInputCmd(MsgType.INITIAL_PASSPHRASE)

    def update(self, msg: Any):
        match msg:
            case TypedStringMsg(
                msg=message,
                msg_type=MsgType.INITIAL_PASSPHRASE,
            ):
                self.state.passphrase = message
                return (self, GetInputCmd(MsgType.GET_PASSPHRASE))
            case TypedStringMsg(
                msg=self.state.passphrase,
                msg_type=MsgType.GET_PASSPHRASE,
            ):
                self.state.correct = True
                return (self, command.Quit())
            case _:
                self.state.attempts += 1
                return (self, GetInputCmd(MsgType.GET_PASSPHRASE))

    def view(self):
        if self.state.passphrase is None:
            print("Enter the passphrase: ", end="")
        elif self.state.attempts == 0 and not self.state.correct:
            print("Now re-enter the passphrase: ", end="")
        elif not self.state.correct:
            print(
                f"Incorrect after {self.state.attempts} attempts, try again: ",
                end="",
            )


async def main():
    lp = loop.Loop(command.NoOp(), 0)
    await lp.run(Model())


if __name__ == "__main__":
    asyncio.run(main())
