import pymssql
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
import logging

class DatabaseInterface(ABC):
    """Database işlemleri için interface"""
    
    @abstractmethod
    def connect(self) -> bool:
        pass
    
    @abstractmethod
    def execute_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def execute_single_query(self, query: str, params: tuple = None) -> Optional[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def close(self) -> None:
        pass

class DatabaseService(DatabaseInterface):
    """SQL Server database bağlantı ve sorgu işlemleri"""
    
    def __init__(self, server: str, user: str, password: str, database: str):
        self.server = server
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        self.logger = logging.getLogger(__name__)
    
    def connect(self) -> bool:
        """Database bağlantısını oluştur"""
        try:
            self.connection = pymssql.connect(
                server=self.server,
                user=self.user,
                password=self.password,
                database=self.database
            )
            return True
        except Exception as e:
            self.logger.error(f"Database bağlantı hatası: {str(e)}")
            return False
    
    def execute_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """Çoklu sonuç dönen sorguları çalıştır"""
        if not self.connection:
            if not self.connect():
                return []
        
        try:
            cursor = self.connection.cursor(as_dict=True)
            cursor.execute(query, params or ())
            results = cursor.fetchall()
            return results
        except Exception as e:
            self.logger.error(f"Query execution error: {str(e)}")
            return []
    
    def execute_single_query(self, query: str, params: tuple = None) -> Optional[Dict[str, Any]]:
        """Tek sonuç dönen sorguları çalıştır"""
        if not self.connection:
            if not self.connect():
                return None
        
        try:
            cursor = self.connection.cursor(as_dict=True)
            cursor.execute(query, params or ())
            result = cursor.fetchone()
            return result
        except Exception as e:
            self.logger.error(f"Single query execution error: {str(e)}")
            return None
    
    def close(self) -> None:
        """Database bağlantısını kapat"""
        if self.connection:
            try:
                self.connection.close()
                self.connection = None
            except Exception as e:
                self.logger.error(f"Connection close error: {str(e)}")
    
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close() 