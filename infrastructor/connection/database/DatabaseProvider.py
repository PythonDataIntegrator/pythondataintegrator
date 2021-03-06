from injector import inject

from domain.connection.services.ConnectionSecretService import ConnectionSecretService
from infrastructor.cryptography.CryptoService import CryptoService
from infrastructor.connection.database.DatabaseContext import DatabaseContext
from infrastructor.connection.database.DatabasePolicy import DatabasePolicy
from infrastructor.dependency.scopes import IScoped
from infrastructor.logging.SqlLogger import SqlLogger
from models.configs.DatabaseConfig import DatabaseConfig
from models.dao.connection.Connection import Connection


class DatabaseProvider(IScoped):
    @inject
    def __init__(self,
                 crypto_service: CryptoService,
                 sql_logger: SqlLogger,
                 database_config: DatabaseConfig,
                 connection_secret_service: ConnectionSecretService
                 ):
        self.connection_secret_service = connection_secret_service
        self.database_config = database_config
        self.sql_logger = sql_logger
        self.crypto_service: CryptoService = crypto_service

    def get_database_context(self, connection: Connection) -> DatabaseContext:
        """
        Creating Connection
        """
        if connection.ConnectionType.Name == 'Database':
            connection_basic_authentication = self.connection_secret_service.get_connection_basic_authentication(
                connection_id=connection.Id)
            if connection.Database.ConnectorType.Name == 'ORACLE':
                user = connection_basic_authentication.User
                password = connection_basic_authentication.Password
                host = connection.Database.Host
                port = connection.Database.Port
                service_name = connection.Database.ServiceName
                sid = connection.Database.Sid
                config = DatabaseConfig(type=connection.Database.ConnectorType.Name, host=host, port=port,
                                        sid=sid, service_name=service_name, username=user, password=password)
            elif connection.Database.ConnectorType.Name == 'MSSQL':
                user = connection_basic_authentication.User
                password = connection_basic_authentication.Password
                host = connection.Database.Host
                port = connection.Database.Port
                database_name = connection.Database.DatabaseName
                config = DatabaseConfig(type=connection.Database.ConnectorType.Name, host=host, port=port,
                                        database=database_name, username=user, password=password)
            elif connection.Database.ConnectorType.Name == 'POSTGRESQL':
                user = connection_basic_authentication.User
                password = connection_basic_authentication.Password
                host = connection.Database.Host
                port = connection.Database.Port
                database_name = connection.Database.DatabaseName
                config = DatabaseConfig(type=connection.Database.ConnectorType.Name, host=host, port=port,
                                        database=database_name, username=user, password=password)

            database_policy = DatabasePolicy(config)
            database_context: DatabaseContext = DatabaseContext(
                database_policy, self.sql_logger)
            return database_context
