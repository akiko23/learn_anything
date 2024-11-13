import os
import pwd
import shutil
import subprocess
import uuid
from datetime import datetime
from pathlib import Path
from typing import Self

import aiofiles

from learn_anything.application.ports.playground import PlaygroundFactory, Playground
from learn_anything.entities.task.models import CodeTask, CodeTaskTest
from learn_anything.entities.user.models import UserID


class UnixPlayground(Playground):
    _playground_base_path: Path = Path('/tmp') / 'playground'
    _playground_user = 'learn_anything'

    def __init__(
            self,
            task: CodeTask,
            user_id: UserID,
            submission_content: str
    ):
        self._task = task
        self._user_id = user_id
        self._submission_content = submission_content

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
        await self._create_playground()
        return self

    async def _create_playground(self):
        self._pl_path = self._generate_playground_path()
        self._pl_path.mkdir(mode=0o777)
        chown_ps = subprocess.Popen(['chown', self._playground_user, self._pl_path])
        chown_ps.wait()

        async with aiofiles.open(self._pl_path / 'task.py', 'w') as f:
            await f.write(self._task.prepared_code)

        # run task prepared code (assume it is safe)
        process = subprocess.Popen(
            ['python3', 'task.py'],
            preexec_fn=self._preexec_fn,
            cwd=str(self._pl_path),
            env=self._env,
        )
        process.wait(timeout=self._task.code_duration_timeout)

        # save user's code
        async with aiofiles.open(self._pl_path / 'main.py', 'w') as f:
            await f.write(self._submission_content)

    def _generate_playground_path(self) -> Path:
        playground_id = uuid.uuid3(uuid.NAMESPACE_OID, f"{self._task.id}_{self._user_id}_{datetime.now()}")
        return self._playground_base_path / Path(str(playground_id))

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        shutil.rmtree(self._pl_path)
        print(exc_type, exc_val, exc_tb)
        # raise exc_type

    def _run_user_submission(self) -> (str, str):
        process = subprocess.Popen(
            ['python3', 'main.py'],
            preexec_fn=self._preexec_fn,
            cwd=str(self._pl_path),
            env=self._env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        process.wait(timeout=self._task.code_duration_timeout)

        out, err = process.communicate()
        return out.decode(), err.decode()

    def _check_test(self, test: CodeTaskTest, user_submission_output: str, user_submission_stderr: str) -> (str, bool):
        # you can use 'stdout' variable to retrieve an output from the user's code
        # and 'stderr' variable to retrieve a stderr from the user's code
        test_code = f'stdout = {user_submission_output}\nstderr = {user_submission_stderr}' + test.code

        process = subprocess.Popen(
            ['python3', '-c', test_code],
            preexec_fn=self._preexec_fn,
            cwd=str(self._pl_path),
            env=self._env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        process.wait(timeout=self._task.code_duration_timeout)

        out, err = process.communicate()
        if err:
            return f"Output:\n{out.decode()}\n{err.decode()}", False

        return out.decode(), True

    def check_submission(self) -> tuple[str, int]:
        out, err = self._run_user_submission()
        for index, test in enumerate(self._task.tests):
            output, passed = self._check_test(
                test=test,
                user_submission_output=out,
                user_submission_stderr=err,
            )
            if not passed:
                return output, index
        return 'ok', -1


def _demote(user_uid, user_gid):
    def result():
        os.setgid(user_gid)
        os.setuid(user_uid)

    return result


class UnixPlaygroundFactory(PlaygroundFactory):
    def create(
            self,
            task: CodeTask,
            user_id: UserID,
            submission_content: str
    ) -> UnixPlayground:
        return UnixPlayground(
            task=task,
            user_id=user_id,
            submission_content=submission_content,
        )
