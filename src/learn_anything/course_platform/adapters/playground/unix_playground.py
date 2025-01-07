import asyncio
import os
import subprocess
import time
import uuid
from concurrent.futures.process import ProcessPoolExecutor
from concurrent.futures.thread import ThreadPoolExecutor
from functools import partial
from pathlib import Path
from signal import Signals
from typing import Self, Any, Optional

import paramiko
from paramiko.common import cMSG_CHANNEL_REQUEST

from learn_anything.course_platform.adapters.logger import logger
from learn_anything.course_platform.application.ports.playground import PlaygroundFactory, Playground, StdErr, StdOut, \
    CodeIsInvalidError


class UnixPlayground(Playground):
    _playground_base_path: Path = Path('/tmp') / 'playground'
    _playground_host = '127.0.0.1'
    _playground_user = 'sandbox'
    _playground_password = 'sandbox'

    def __init__(
            self,
            identifier: str | None,
            code_duration_timeout: int
    ) -> None:
        self._id = identifier
        self._code_duration_timeout = code_duration_timeout
        self._vm: VirtualMachineFacade | None = None
        self._ssh_client = paramiko.SSHClient()

    async def __aenter__(self) -> Self:
        await self._create_playground()
        return self

    async def _create_playground(self):
        loop = asyncio.get_running_loop()
        with ProcessPoolExecutor() as ps_pool:
            self._vm = await loop.run_in_executor(
                ps_pool,
                VirtualMachineFacade(id_=self._id).create,
            )

        self._ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        with ThreadPoolExecutor(max_workers=4) as th_pool:
            await loop.run_in_executor(
                th_pool,
                partial(
                    self._ssh_client.connect,
                    hostname=self._playground_host,
                    port=self._vm.exposed_ssh_port,
                    username=self._playground_user,
                    password=self._playground_password,
                    banner_timeout=200,
                )
            )
        logger.info('Successfully connected to vm %s via ssh', self._id)

    async def execute_code(self, code: str, raise_exc_on_err: bool = False) -> tuple[StdOut, StdErr]:
        loop = asyncio.get_running_loop()

        with ThreadPoolExecutor() as th_pool:
            out, err = await loop.run_in_executor(
                th_pool,
                self._execute_code,
                code
            )
            if err and raise_exc_on_err:
                raise CodeIsInvalidError(code=code, out=out, err=err)

        return out, err

    def _execute_code(self, code: str) -> tuple[StdOut, StdErr]:
        out, err = b'', b''
        try:
            logger.info('Sending command..')
            stdin, stdout, stderr = self._ssh_client.exec_command(
                f'echo -e "{code}" | python3',
            )

            start = time.time()
            while time.time() - start < self._code_duration_timeout + 1:
                if stdin.channel.exit_status_ready():
                    out_data = stdout.read().decode().strip()
                    err_data = stderr.read().decode().strip()

                    logger.warning('Data: stdout - %s, stderr - %s', out_data, err_data)
                    return (
                        StdOut(out_data),
                        StdErr(err_data)
                    )
                time.sleep(0.5)

            message = paramiko.Message()
            message.add_byte(cMSG_CHANNEL_REQUEST)
            message.add_int(stdin.channel.remote_chanid)
            message.add_string("signal")
            message.add_boolean(False)
            message.add_string(Signals.SIGINT.name[3:])
            stdin.channel.transport._send_user_message(message)

            logger.info('Sent SIGINT to stdin channel')

            out = stdout.read()
            err = stderr.read()
            raise TimeoutError
        except TimeoutError:
            return (
                StdOut(out.decode() + '\n' + err.decode()),
                StdErr(f'TimeoutError: your code timed out after {self._code_duration_timeout} seconds')
            )
        except Exception as e:
            logger.error('Error during code execution: %s', str(e))

    async def __aexit__(self, exc_type: type[Exception], exc_val: Any, exc_tb: str) -> None:
        with ThreadPoolExecutor(max_workers=3) as th_pool:
            th_pool.submit(self._ssh_client.close)

        with ProcessPoolExecutor(max_workers=2) as ps_pool:
            ps_pool.submit(self._vm.delete)

        if exc_type:
            logger.error('An error of type %s with val %s occurred: %s', exc_type, exc_val, exc_tb)


class VirtualMachineFacade:
    image_storage_base_path = os.path.join('/etc', 'learn_anything', 'qemu_disk_images')
    base_disk_image_path = os.path.join(image_storage_base_path, 'debian12-2_python_base.qcow2')
    create_vm_script_path = os.path.join('/etc', 'learn_anything', 'scripts', 'create_qemu_vm.sh')
    get_free_port_script_path = os.path.join('/etc', 'learn_anything', 'scripts', 'get_available_port.sh')

    def __init__(self, id_: Optional[str] = None, disk_image_path: Optional[str] = None, port: Optional[int] = None):
        self._id = id_ or str(uuid.uuid4())
        self._vm_pid = None
        self._disk_image_path = disk_image_path
        self._port = port

    def create(self) -> Self:
        if self._disk_image_path is None:
            self._disk_image_path = self._init_disk_image()

        if self._port is None:
            self._port = self._get_free_port()

        logger.info('Creating vm..')
        create_vm_ps = subprocess.Popen(
            [self.create_vm_script_path, str(self._port), self._disk_image_path],
            start_new_session=True,
        )

        logger.info('Now waiting for its init..')
        time.sleep(2)
        logger.info('Created vm..')

        self._vm_pid = create_vm_ps.pid
        return self

    @property
    def exposed_ssh_port(self):
        return self._port

    def _init_disk_image(self) -> str:
        disk_image_copies_path = os.path.join(
            self.image_storage_base_path,
            f'debian12_python_{self._id}.qcow2',
        )

        image_path = disk_image_copies_path.format()
        create_img_ps = subprocess.Popen(
            ['qemu-img', 'create', '-f', 'qcow2', '-b', self.base_disk_image_path, '-F', 'qcow2', image_path]
        )
        create_img_ps.wait()

        return image_path

    def delete(self):
        if not self._vm_pid:
            raise Exception('There is nothing to delete')

        kill_vm_ps = subprocess.Popen(
            ['pkill', '-s', str(os.getsid(self._vm_pid)), '--signal', 'KILL'],
        )
        kill_vm_ps.wait()

        os.system(f'rm -f {self._disk_image_path}')

    def _get_free_port(self) -> int:
        ps = subprocess.Popen(
            self.get_free_port_script_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True,
            shell=True,
        )
        out, _ = ps.communicate()
        return int(out.decode().strip())


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
