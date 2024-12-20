import asyncio
import logging
import os
import pwd
import resource
import shutil
import subprocess
import uuid
from concurrent.futures.process import ProcessPoolExecutor
from contextlib import suppress
from datetime import datetime
from pathlib import Path
from subprocess import TimeoutExpired
from typing import Self, Any

from learn_anything.course_platform.application.ports.playground import PlaygroundFactory, Playground, StdErr, StdOut, \
    CodeIsInvalidError

logger = logging.getLogger(__name__)


class UnixPlayground(Playground):
    _playground_base_path: Path = Path('/tmp') / 'playground'
    _playground_user = 'learn_anything'

    def __init__(
            self,
            identifier: str | None,
            code_duration_timeout: int
    ) -> None:
        self._pl_path = self._generate_playground_path(additional_identifier=identifier)
        self._code_duration_timeout = code_duration_timeout

        self._apply_playground_user()

    def _apply_playground_user(self) -> None:
        pw_record = pwd.getpwnam(self._playground_user)
        user_home_dir = pw_record.pw_dir

        self._env = os.environ.copy()
        self._env['HOME'] = user_home_dir
        self._env['LOGNAME'] = self._playground_user
        self._env['PWD'] = str(self._playground_base_path)
        self._env['USER'] = self._playground_user

    async def __aenter__(self) -> Self:
        self._pl_path.mkdir(parents=True, mode=0o777)
        chown_ps = subprocess.Popen(['chown', self._playground_user, self._pl_path])
        chown_ps.wait()

        return self

    # todo: add MVM
    async def execute_code(self, code: str, raise_exc_on_err: bool = False) -> tuple[StdOut, StdErr]:
        loop = asyncio.get_running_loop()

        with ProcessPoolExecutor() as pool:
            out, err = await loop.run_in_executor(
                pool,
                self._execute_code,
                code
            )
            if err and raise_exc_on_err:
                raise CodeIsInvalidError(code=code, out=out, err=err)

        return out, err

    def _execute_code(self, code: str) -> tuple[StdOut, StdErr]:
        process = subprocess.Popen(
            ['python3', '-c', code],
            preexec_fn=_demote,
            cwd=str(self._pl_path),
            env=self._env,
            user=self._playground_user,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True,
        )

        try:
            out, err = process.communicate(timeout=self._code_duration_timeout)
        except TimeoutExpired:
            self._kill_derivatives(process.pid)

            out, err = process.communicate()

            logger.warning('Playground user processes were successfully killed')

            return (
                StdOut(out.decode() + '\n' + err.decode()),
                StdErr(f'TimeoutError: \'{code}\' timed out after {self._code_duration_timeout} seconds')
            )

        with suppress(ProcessLookupError):
            self._kill_derivatives(process.pid)

        return StdOut(out.decode().strip()), StdErr(err.decode().strip())

    @staticmethod
    def _kill_derivatives(pid: int) -> None:
        kill_process = subprocess.Popen(
            ['pkill', '-s', str(os.getsid(pid)), '--signal', 'KILL'],
        )
        kill_process.wait()

    async def __aexit__(self, exc_type: type[Exception], exc_val: Any, exc_tb: str) -> None:
        shutil.rmtree(self._pl_path)
        if exc_type:
            logger.error('An error of type %s with val %s occurred: %s', exc_type, exc_val, exc_tb)

    def _generate_playground_path(self, additional_identifier: str | None) -> Path:
        playground_id = uuid.uuid4()
        if additional_identifier is not None:
            playground_id = uuid.uuid3(uuid.NAMESPACE_OID, f'{additional_identifier}_{datetime.now()}')
        return self._playground_base_path / Path(str(playground_id))


ADDRESS_SPACE_LIMITS = (1024 * 1024 * 500, 1024 * 1024 * 500)
NPROC_LIMITS = (50, 50)

def _demote() -> None:
    resource.prlimit(
        os.getpid(),
        resource.RLIMIT_NPROC,
        NPROC_LIMITS
    )

    resource.setrlimit(
        resource.RLIMIT_AS,
        ADDRESS_SPACE_LIMITS
    )


class UnixPlaygroundFactory(PlaygroundFactory):
    def create(
            self,
            code_duration_timeout: int,
            identifier: str | None = None,
    ) -> UnixPlayground:
        return UnixPlayground(
            identifier=identifier,
            code_duration_timeout=code_duration_timeout,
        )
