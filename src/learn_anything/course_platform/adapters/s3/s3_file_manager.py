import asyncio
from concurrent.futures.thread import ThreadPoolExecutor
from io import BytesIO
from pathlib import Path

from minio import Minio, S3Error
from minio.commonconfig import Tags
from urllib3.response import BaseHTTPResponse

from learn_anything.course_platform.adapters.s3.config import S3Config
from learn_anything.course_platform.application.ports.data.file_manager import FileManager, FilePath, DirTree


class S3FileManager(FileManager):
    def __init__(self, config: S3Config) -> None:
        self._config = config
        self._client = Minio(
            endpoint=config.endpoint_url,
            access_key=config.access_key,
            secret_key=config.secret_key,
            secure=False,
        )
        self._init_buckets()
        self._upload_defaults()

    # will be removed in the future
    def _init_buckets(self) -> None:
        if not self._client.bucket_exists('courses'):
            self._create_bucket(name='courses')

        if not self._client.bucket_exists('defaults'):
            self._create_bucket(name='defaults')

    def _upload_defaults(self) -> None:
        bucket_name = 'defaults'
        file_name = 'course_default_img.jpg'

        try:
            self._client.get_object(bucket_name=bucket_name, object_name=file_name)
        except S3Error:
            path = str(Path(bucket_name) / file_name)
            with open(path, 'rb') as file_obj:
                file_content = file_obj.read()

                tags = Tags.new_object_tags()
                tags['id'] = 'null'
                with BytesIO(file_content) as buffer:
                    self._client.put_object(
                        bucket_name,
                        file_name,
                        buffer,
                        len(file_content),
                        tags=tags
                    )

    def _create_bucket(self, name: str) -> None:
        self._client.make_bucket(name)

    def generate_path(self, directories: tuple[str] | str, filename: str) -> FilePath:
        bucket = directories if isinstance(directories, str) else directories[0]
        filename = filename if isinstance(directories, str) else '/'.join([*directories[1:], filename])

        return FilePath(f'{bucket}/{filename}')

    async def get_props_by_path(self, path: FilePath) -> tuple[DirTree, str]:
        bucket_name, file_name = self._parse_path(path=path)
        if bucket_name != 'defaults':
            return DirTree((bucket_name,)), file_name

        loop = asyncio.get_running_loop()
        with ThreadPoolExecutor() as executor:
            tags = await loop.run_in_executor(
                executor,
                self._client.get_object_tags,
                bucket_name,
                file_name
            )

        if not tags:
            raise ValueError(f'Object in path: \'{path}\' has no tags')

        return DirTree((bucket_name,)), str(tags['id'])

    @staticmethod
    def _parse_path(path: FilePath) -> tuple[str, str]:
        bucket_name, file_name = path.split('/')[0], '/'.join(path.split('/')[1:])
        return bucket_name, file_name

    async def update(self, old_file_path: FilePath, new_file_path: FilePath, payload: bytes | None) -> None:
        bucket_name, file_name = self._parse_path(path=old_file_path)
        if bucket_name == 'defaults':
            tags = self._client.get_object_tags(bucket_name=bucket_name, object_name=file_name)
            if not tags:
                raise ValueError(f'Object in path: \'{old_file_path}\' has no tags')

            _, new_file_id = self._parse_path(path=new_file_path)
            tags['id'] = new_file_id
            self._client.set_object_tags(bucket_name=bucket_name, object_name=file_name, tags=tags)
            return

        if payload is None:
            await self._client.remove_object(bucket_name=bucket_name, object_name=file_name)
            return

        loop = asyncio.get_running_loop()
        with ThreadPoolExecutor(max_workers=2) as executor:
            del_obj_fut = loop.run_in_executor(executor, self._client.remove_object, bucket_name, file_name)
            with BytesIO(payload) as file_obj:
                put_obj_fut = loop.run_in_executor(
                    executor,
                    self._client.put_object,
                    bucket_name,
                    file_name,
                    file_obj,
                    len(payload)
                )

                await asyncio.wait([del_obj_fut, put_obj_fut], return_when=asyncio.ALL_COMPLETED)

    async def save(self, payload: bytes, file_path: FilePath) -> None:
        bucket_name, file_name = self._parse_path(path=file_path)

        loop = asyncio.get_running_loop()
        with ThreadPoolExecutor(max_workers=2) as executor:
            with BytesIO(payload) as file_obj:
                bucket_exists = await loop.run_in_executor(
                    executor,
                    self._client.bucket_exists,
                    bucket_name
                )
                if not bucket_exists:
                    await loop.run_in_executor(
                        executor,
                        self._create_bucket,
                        bucket_name
                    )

                await loop.run_in_executor(
                    executor,
                    self._client.put_object,
                    bucket_name,
                    file_name,
                    file_obj,
                    len(payload),
                )

    async def get_by_file_path(self, file_path: FilePath) -> BaseHTTPResponse | None:
        bucket_name, file_id = self._parse_path(path=file_path)
        try:
            loop = asyncio.get_running_loop()
            with ThreadPoolExecutor(max_workers=2) as executor:
                obj = await loop.run_in_executor(
                    executor,
                    self._client.get_object,
                    bucket_name, file_id
                )
        except S3Error:
            obj = None
        return obj

    async def delete_folder(self, name: str) -> None:
        self._client.remove_bucket(bucket_name=name)

    async def delete(self, file_path: FilePath) -> None:
        bucket_name, file_id = self._parse_path(path=file_path)

        loop = asyncio.get_running_loop()
        with ThreadPoolExecutor(max_workers=2) as executor:
            await loop.run_in_executor(executor, self._client.remove_object, bucket_name, file_id)
