from . import protocol as p


# Messages
class EmptyMsg:
    def __init__(self):
        pass


class ExitMsg:
    def __init__(self):
        pass


# Commands
class PassMsg:
    """
    A command with a default execution that just returns the instance level `msg`.
    """

    def __init__(self, msg: p.Msg):
        self.msg = msg

    async def exec(self):
        return self.msg


class NoOp(PassMsg):
    """
    A command that does nothing. Acts as a nice placeholder if you must have a command not equal to `None`.
    """

    def __init__(self):
        super().__init__(EmptyMsg())


class Quit(PassMsg):
    """
    `Loop.run` looks for this command and will exit the loop when detected.  Any `await` calls on `Loop.run` will complete.

    See also::
        :meth:`loop.Loop.run`
    """

    def __init__(self):
        super().__init__(ExitMsg())
