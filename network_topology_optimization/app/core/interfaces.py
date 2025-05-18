from abc import ABC, abstractmethod

class IStorageManager(ABC):
    @abstractmethod
    def save_uploaded_file(self, file, query_id: str) -> str: ...

    @abstractmethod
    def save_final_result(self, content: bytes, query_id: str) -> str: ...

    @abstractmethod
    def cleanup_query_files(self,query_id: str): ...

class IProcessManager(ABC):
    @abstractmethod
    def process(self, input: list) -> list: ...