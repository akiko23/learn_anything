import os.path
from urllib3.response import BaseHTTPResponse
from io import BytesIO

from minio import Minio

from learn_anything.application.ports.data.file_manager import FileManager
from learn_anything.adapters.s3.config import S3Config


class S3FileManager(FileManager):
    def __init__(self, config: S3Config):
        self._config = config
        self._client = Minio(
            endpoint=config.endpoint_url,
            access_key=config.access_key,
            secret_key=config.secret_key,
            secure=False,
        )
        self._init_buckets()

    # will be removed in the future
    def _init_buckets(self):
        if not self._client.bucket_exists('courses'):
            self._create_bucket(name='courses')

    def _create_bucket(self, name: str) -> None:
        self._client.make_bucket(bucket_name=name)

    @staticmethod
    def _parse_path(path: str):
        bucket_name, file_id = os.path.split(path)
        return bucket_name, file_id

    def save(self, payload: bytes, file_path: str) -> None:
        with BytesIO(payload) as file_obj:
            bucket_name, file_id = self._parse_path(path=file_path)

            if not self._client.bucket_exists(bucket_name=bucket_name):
                self._create_bucket(name=bucket_name)
            self._client.put_object(
                bucket_name=bucket_name,
                object_name=file_id,
                data=file_obj,
                length=len(payload),
            )

    def get_by_file_path(self, file_path: str) -> BaseHTTPResponse | None:
        bucket_name, file_id = self._parse_path(path=file_path)
        obj = self._client.get_object(bucket_name=bucket_name, object_name=file_id)

        if not obj:
            return None
        return obj

    def delete_folder(self, name: str) -> None:
        self._client.remove_bucket(bucket_name=name)

    def delete(self, file_path: str) -> None:
        bucket_name, file_id = self._parse_path(path=file_path)
        self._client.remove_object(bucket_name=bucket_name, object_name=file_id)