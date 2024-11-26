import logging
import os
import pwd
import resource
import shutil
import subprocess
import uuid
from contextlib import suppress
from datetime import datetime
from pathlib import Path
from subprocess import TimeoutExpired
from typing import Self

from learn_anything.application.ports.playground import PlaygroundFactory, Playground

logger = logging.getLogger(__name__)


class UnixPlayground(Playground):
    _playground_base_path: Path = Path('/tmp') / 'playground'
    _playground_user = 'learn_anything'

    def __init__(
            self,
            identifier: str | None,
            code_duration_timeout: int
    ):
        self._code_duration_timeout = code_duration_timeout
        self._pl_path = self._generate_playground_path(additional_identifier=identifier)

        self._apply_playground_user()

    def _apply_playground_user(self):
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

    # todo: replace with MVM
    async def execute_code(self, code: str) -> (str, str):
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
                out.decode() + '\n' + err.decode(),
                f'TimeoutError: \'{code}\' timed out after {self._code_duration_timeout} seconds'
            )

        with suppress(ProcessLookupError):
            self._kill_derivatives(process.pid)

        return out.decode().strip(), err.decode().strip()

    @staticmethod
    def _kill_derivatives(pid):
        kill_process = subprocess.Popen(
            ['pkill', '-s', str(os.getsid(pid)), '--signal', 'KILL'],
        )
        kill_process.wait()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        shutil.rmtree(self._pl_path)
        if exc_type:
            logger.error('An error of type %s with val %s occurred: %s', exc_type, exc_val, exc_tb)

    def _generate_playground_path(self, additional_identifier) -> Path:
        playground_id = uuid.uuid4()
        if additional_identifier is not None:
            playground_id = uuid.uuid3(uuid.NAMESPACE_OID, f'{additional_identifier}_{datetime.now()}')
        return self._playground_base_path / Path(str(playground_id))


def _demote():
    resource.prlimit(
        os.getpid(),
        resource.RLIMIT_NPROC,
        (50, 50)
    )


class UnixPlaygroundFactory(PlaygroundFactory):
    def create(
            self,
            code_duration_timeout: int,
            identifier: str | None = None,
    ) -> UnixPlayground:
        return UnixPlayground(
            identifier=identifier,
            code_duration_timeout=code_duration_timeout
        )
