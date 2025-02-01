import asyncio
from typing import Tuple

from . import command, protocol as p


class Loop:
    """
    A command loop runner for a given model and default command.
    """

    def __init__(self, default_cmd: p.Cmd, task_timeout: float):
        """
        Create a new command loop.

        Args:
            default_cmd: The default command to execute if no commands are available to run.
            task_timeout: The timeout to wait for a command to complete.
        """
        self.default_cmd = default_cmd
        self.task_timeout = task_timeout
        self.__tasks: set[asyncio.Task[p.Msg]] = set()

    def __shutdown(self):
        for t in self.__tasks:
            t.cancel()

    def __must_quit(self, commands: list[p.Cmd]) -> bool:
        for cmd in commands:
            if isinstance(cmd, command.Quit):
                return True
        return False

    def __queue_tasks(self, commands: list[p.Cmd]):
        for cmd in commands:
            task = asyncio.create_task(cmd.exec())
            self.__tasks.add(task)

    def __handle_tasks(
        self,
        model: p.Model,
        tasks: set[asyncio.Task[p.Msg]],
    ) -> Tuple[p.Model, list[p.Cmd]]:
        next_model = model
        next_commands: list[p.Cmd] = []

        completed_tasks = [t for t in tasks if t.done()]
        for t in completed_tasks:
            msg = t.result()
            self.__tasks.remove(t)
            next_model, cmd = model.update(msg)
            if cmd is not None:
                next_commands.append(cmd)
            next_model.view()

        return next_model, next_commands

    async def run(self, model: p.Model):
        """
        Run the loop for the given model.

        Args:
            model: The model to run the loop against.
        """
        model.view()

        commands: list[p.Cmd] = []
        init_cmd = model.init()
        if init_cmd is not None:
            commands.append(init_cmd)

        while not self.__must_quit(commands):
            if len(commands) == 0:
                commands.append(self.default_cmd)

            self.__queue_tasks(commands)

            completed_tasks, _ = await asyncio.wait(
                self.__tasks,
                timeout=self.task_timeout,
                return_when=asyncio.FIRST_COMPLETED,
            )

            model, commands = self.__handle_tasks(model, completed_tasks)

        self.__shutdown()
