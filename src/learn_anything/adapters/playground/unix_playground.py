import os
import pwd
import shutil
import subprocess
import uuid
from datetime import datetime
from pathlib import Path
from typing import Self

from learn_anything.application.ports.playground import PlaygroundFactory, Playground


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
        user_uid = pw_record.pw_uid
        user_gid = pw_record.pw_gid

        self._env = os.environ.copy()
        self._env['HOME'] = user_home_dir
        self._env['LOGNAME'] = self._playground_user
        self._env['PWD'] = str(self._playground_base_path)
        self._env['USER'] = self._playground_user

        self._preexec_fn = _demote(user_uid, user_gid)

    async def __aenter__(self) -> Self:
        self._pl_path.mkdir(parents=True, mode=0o777)
        chown_ps = subprocess.Popen(['chown', self._playground_user, self._pl_path])
        chown_ps.wait()

        return self

    async def execute_code(self, code: str) -> (str, str):
        process = subprocess.Popen(
            ['python3', '-c', code],
            preexec_fn=self._preexec_fn,
            cwd=str(self._pl_path),
            env=self._env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        process.wait(timeout=self._code_duration_timeout)

        out, err = process.communicate()
        return out.decode(), err.decode()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        shutil.rmtree(self._pl_path)
        print(exc_type, exc_val, exc_tb)
        # raise exc_type

    def _generate_playground_path(self, additional_identifier) -> Path:
        playground_id = uuid.uuid4()
        if additional_identifier is not None:
            playground_id = uuid.uuid3(uuid.NAMESPACE_OID, f'{additional_identifier}_{datetime.now()}')
        return self._playground_base_path / Path(str(playground_id))


def _demote(user_uid, user_gid):
    def result():
        os.setgid(user_gid)
        os.setuid(user_uid)

    return result


class UnixPlaygroundFactory(PlaygroundFactory):
    def create(
            self,
            identifier: str | None,
            code_duration_timeout: int
    ) -> UnixPlayground:
        return UnixPlayground(
            identifier=identifier,
            code_duration_timeout=code_duration_timeout
        )

