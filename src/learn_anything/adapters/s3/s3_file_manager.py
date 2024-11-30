import os.path
from urllib3.response import BaseHTTPResponse
from io import BytesIO

from minio import Minio, S3Error

from learn_anything.application.ports.data.file_manager import FileManager, FilePath
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

    def generate_path(self, directories: tuple[str], filename: str) -> FilePath:
        return f'{directories[0]}/{filename}'

    def parse_path(self, path: FilePath) -> (str, str):
        bucket_name, file_id = os.path.split(path)
        return bucket_name, file_id

    def save(self, payload: bytes, file_path: FilePath) -> None:
        with BytesIO(payload) as file_obj:
            bucket_name, file_id = self.parse_path(path=file_path)

            if not self._client.bucket_exists(bucket_name=bucket_name):
                self._create_bucket(name=bucket_name)
            self._client.put_object(
                bucket_name=bucket_name,
                object_name=file_id,
                data=file_obj,
                length=len(payload),
            )

    def get_by_file_path(self, file_path: FilePath) -> BaseHTTPResponse | None:
        bucket_name, file_id = self.parse_path(path=file_path)
        try:
            obj = self._client.get_object(bucket_name=bucket_name, object_name=file_id)
        except S3Error:
            obj = None
        return obj

    def delete_folder(self, name: str) -> None:
        self._client.remove_bucket(bucket_name=name)

    def delete(self, file_path: FilePath) -> None:
        bucket_name, file_id = self.parse_path(path=file_path)
        self._client.remove_object(bucket_name=bucket_name, object_name=file_id)
