import subprocess
from subprocess import PIPE, CompletedProcess


def run_command(command: str,
                expected_program_name: str,
                path: str) -> CompletedProcess:
    """
    Run a shell command and return the results.

    :param command: string with a command to run.
    :param expected_program_name: string with a name of a program
     which should be called.
    :param path: string with a path where a program should run.
    :return: CompletedProcess which contains input arguments,
     returncode, stdout, and stderr.

    >>> run_command("echo Hello World", "echo", ".")
    CompletedProcess(args=['echo', 'Hello World'], returncode=0, \
stdout=b'Hello World\\n', stderr=b'')

    >>> run_command("", "echo", ".")
    CompletedProcess(args=[], returncode=0, stdout='', stderr='')

    >>> run_command("echo Hello World", "cat", ".")
    CompletedProcess(args=[], returncode=0, stdout='', stderr='')

    >>> run_command("echo Hello World", "", ".")
    Traceback (most recent call last):
      ...
    ValueError: Expected command string is empty.

    >>> run_command("=", "=", ".")
    Traceback (most recent call last):
      ...
    FileNotFoundError: [Errno 2] No such file or directory: '=': '='

    >>> run_command("=", "=", "asdf")
    Traceback (most recent call last):
      ...
    FileNotFoundError: [Errno 2] No such file or directory: 'asdf': 'asdf'
    """

    if not expected_program_name:
        raise ValueError("Expected command string is empty.")

    if not command:
        return CompletedProcess(args=[], returncode=0, stdout="", stderr="")

    split_command: [str] = command.split(" ", 1)

    program_name: str = split_command[0]
    program_args: str = ""

    if program_name != expected_program_name:
        return CompletedProcess(args=[], returncode=0, stdout="", stderr="")

    if len(split_command) > 1:
        program_args: str = split_command[1]

    # Run program and return stdout and stderr
    # in addition to arguments and returncode
    return subprocess.run([program_name, program_args],
                          stdout=PIPE,
                          stderr=PIPE,
                          cwd=path)


if __name__ == "__main__":
    import doctest

    doctest.testmod()
