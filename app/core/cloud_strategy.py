from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from enum import Enum
from typing import TypeVar

from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions, ResourceTypes, \
    AccountSasPermissions
from fastapi import UploadFile
from google.cloud import storage

from app.core.config import settings

T = TypeVar('T')


class CloudEnum(str, Enum):
    AZURE = 'AZURE'
    GCP = 'GCP'


class CloudDocumentStatus(int, Enum):
    NOT_ACTIVE = 0
    ACTIVE = 1
    IN_PROGRESS = 2
    ERROR = 3


class StrategyException(Exception):
    pass


class ClientCloud:
    instance: T

    # cloud_storage.py: Bucket

    def __init__(self, instance):
        self.instance = instance


class DocumentSave:
    source_file_path: str
    destination_file_path: str
    cloud_process: str

    def __init__(self, source_file_path, destination_file_path, cloud_process):
        self.source_file_pat = source_file_path
        self.destination_file_path = destination_file_path
        self.cloud_process = cloud_process


class Document:
    filename: str
    file_content: bytes
    cloud_process: str


class Strategy(ABC):
    @abstractmethod
    def connect_cloud(self, container: str) -> ClientCloud:
        pass

    @abstractmethod
    def upload_file(self, upload_file: UploadFile, destination_file_path, container: str) -> DocumentSave:
        pass

    @abstractmethod
    def upload_bytes(self, buffer: bytes, destination_file_path, container: str) -> DocumentSave:
        pass

    @abstractmethod
    def get_file(self, relative_url: str, container: str) -> bool:
        pass

    @abstractmethod
    def get_file_sas(self, relative_url: str, container: str, expiry_minutes: int = 10) -> str:
        pass

    @abstractmethod
    def set_client(self, client):
        pass


class CloudContext:
    is_connected: bool = False
    client: any = False

    def __init__(self, strategy: Strategy) -> None:
        self._strategy = strategy

    @property
    def strategy(self) -> Strategy:
        return self._strategy

    @strategy.setter
    def strategy(self, strategy: Strategy) -> None:
        self._strategy = strategy

    def upload_file(self, upload_file: UploadFile, destination_file_path: str, container: str) -> DocumentSave:
        if self.is_connected is False:
            self.client = self._strategy.connect_cloud(container)
            self._strategy.set_client(self.client)
            self.is_connected = True
        return self._strategy.upload_file(upload_file, destination_file_path, container)

    def upload_bytes(self, buffer: bytes, destination_file_path: str, container: str) -> DocumentSave:
        if self.is_connected is False:
            self.client = self._strategy.connect_cloud(container)
            self._strategy.set_client(self.client)
            self.is_connected = True
        return self._strategy.upload_bytes(buffer, destination_file_path, container)

    def get_file(self, relative_path: str, container: str):
        if self.is_connected is False:
            self.client = self._strategy.connect_cloud(container)
            self._strategy.set_client(self.client)
            self.is_connected = True
        return self._strategy.get_file(relative_path, container)

    def get_url_file(self, relative_path: str, container: str, expiry_minutes: int = 10) -> str:
        if self.is_connected is False:
            self.client = self._strategy.connect_cloud(container)
            self._strategy.set_client(self.client)
            self.is_connected = True
        return self._strategy.get_file_sas(relative_path, container, expiry_minutes)


class GcpBucketStrategy(Strategy):
    client: ClientCloud = None
    credentials: str

    def set_client(self, client):
        self.client = client

    def connect_cloud(self, container: str) -> ClientCloud:
        try:
            storage_client = storage.Client.from_service_account_json(self.__get_credentials())
        except Exception as e:
            print(e)
            raise StrategyException({"message": "GCP please check valid credentials "})
        return ClientCloud(
            instance=storage_client.bucket(settings.GCP_BUCKET_NAME)
        )

    def upload_file(self, origin: UploadFile, destination: str, container: str) -> DocumentSave:
        if self.client is None:
            raise StrategyException({"message": "client not connected please verify status"})
        blob = self.client.instance.blob(destination)
        blob.upload_from_filename(origin)
        doc = DocumentSave(
            source_file_path=origin,
            destination_file_path=destination,
            cloud_process=CloudEnum.GCP
        )
        return doc

    def upload_bytes(self, buffer: bytes, destination_file_path: str, container: str) -> DocumentSave:
        if self.client is None:
            raise StrategyException({"message": "client not connected please verify status"})
        blob = self.client.instance.blob(destination_file_path)
        blob.upload_from_string(buffer)
        doc = DocumentSave(
            source_file_path=destination_file_path,
            destination_file_path=destination_file_path,
            cloud_process=CloudEnum.GCP
        )
        return doc

    def get_file_sas(self, relative_url: str, container: str, expiry_minutes: int = 10) -> str:
        return ''

    def get_file(self, relative_url: str, container: str) -> bytes:
        blob = self.client.instance.blob(relative_url)
        return blob.download_as_bytes()

    def __get_credentials(self) -> str:
        credentials = settings.GCP_PATH_JSON_CREDENTIALS
        if credentials is None or credentials.strip() == '':
            raise StrategyException(
                {"message": "GCP CREDENTIALS not load, please check env 'GCP_PATH_JSON_CREDENTIALS'"}
            )
        self.credentials = credentials
        return credentials


class AzureBlobStrategy(Strategy):
    client: ClientCloud = 'instance azure blob'
    service: BlobServiceClient

    def set_client(self, client):
        self.client = client

    def connect_cloud(self, container: str) -> ClientCloud:
        service = BlobServiceClient.from_connection_string(conn_str=settings.blob_storage_connection)
        container_client = service.get_container_client(container=container)
        self.service = service
        return ClientCloud(
            instance=container_client
        )

    def upload_file(self, upload_file: UploadFile, destination: str, container: str) -> DocumentSave:
        if self.client is None:
            raise StrategyException({"message": "client azure not connected"})
        blob_client = self.client.instance.upload_blob(name=destination, data=upload_file.file)

        doc = DocumentSave(
            source_file_path=upload_file,
            destination_file_path=destination,
            cloud_process=CloudEnum.AZURE
        )
        return doc

    def upload_bytes(self, buffer: bytes, destination_file_path: str, container: str) -> DocumentSave:
        if self.client is None:
            raise StrategyException({"message": "client azure not connected"})
        blob_client = self.client.instance.upload_blob(name=destination_file_path, data=buffer)
        doc = DocumentSave(
            source_file_path=destination_file_path,
            destination_file_path=destination_file_path,
            cloud_process=CloudEnum.AZURE
        )
        return doc

    def get_file(self, relative_url: str, container: str):
        blob = self.client.instance.get_blob_client(blob=relative_url)
        return blob.download_blob().readall()

    def get_file_sas(self, relative_url: str, container: str, expiry_minutes: int = 10) -> str:
        sas_token = generate_blob_sas(
            account_name=self.service.account_name,
            container_name=container,
            blob_name=relative_url,
            account_key=self.service.credential.account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(minutes=expiry_minutes),
            resource_types=ResourceTypes(object=True),
            account_permissions=AccountSasPermissions(read=True)
        )
        blob_url_with_sas = f"https://{self.service.account_name}.blob.core.windows.net/{container}/{relative_url}?" + sas_token
        return blob_url_with_sas
