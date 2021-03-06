from injector import inject

from domain.integration.services.DataIntegrationConnectionService import DataIntegrationConnectionService
from domain.operation.execution.adapters.execution.ExecuteAdapter import ExecuteAdapter
from domain.operation.execution.services.IntegrationExecutionService import IntegrationExecutionService
from domain.operation.execution.processes.ExecuteIntegrationProcess import ExecuteIntegrationProcess
from domain.operation.services.DataOperationIntegrationService import DataOperationIntegrationService
from domain.operation.services.DataOperationJobExecutionIntegrationService import \
    DataOperationJobExecutionIntegrationService
from infrastructor.dependency.scopes import IScoped
from infrastructor.logging.SqlLogger import SqlLogger
from models.enums.events import EVENT_EXECUTION_INTEGRATION_EXECUTE_OPERATION


class ExecuteIntegrationAdapter(ExecuteAdapter, IScoped):
    @inject
    def __init__(self,
                 sql_logger: SqlLogger,
                 data_operation_integration_service: DataOperationIntegrationService,
                 data_operation_job_execution_integration_service: DataOperationJobExecutionIntegrationService,
                 data_integration_connection_service: DataIntegrationConnectionService,
                 integration_execution_service: IntegrationExecutionService,
                 execute_integration_process: ExecuteIntegrationProcess):
        self.execute_integration_process = execute_integration_process
        self.integration_execution_service = integration_execution_service
        self.sql_logger = sql_logger
        self.data_integration_connection_service = data_integration_connection_service
        self.data_operation_integration_service = data_operation_integration_service
        self.data_operation_job_execution_integration_service = data_operation_job_execution_integration_service

    def execute(self,
                data_operation_integration_id: int,
                data_operation_job_execution_id: int,
                data_operation_job_execution_integration_id: int) -> int:
        data_operation_integration = self.data_operation_integration_service.get_by_id(
            id=data_operation_integration_id)
        data_integration_id = data_operation_integration.DataIntegrationId
        data_count = self.integration_execution_service.get_source_data_count(
            data_operation_job_execution_integration_id=data_operation_job_execution_integration_id,
            data_integration_id=data_integration_id)
        self.integration_execution_service.clear_data(
            data_operation_job_execution_integration_id=data_operation_job_execution_integration_id,
            data_integration_id=data_integration_id)
        affected_row_count = self.execute_integration(
            data_operation_job_execution_id=data_operation_job_execution_id,
            data_operation_job_execution_integration_id=data_operation_job_execution_integration_id,
            data_operation_integration_id=data_operation_integration_id,
            data_count=data_count)
        if affected_row_count < 0:
            affected_row_count = data_count
        return affected_row_count

    def get_start_log(self, data_integration_id: int):
        target_connection = self.data_integration_connection_service.get_target_connection(
            data_integration_id=data_integration_id)
        return f"{target_connection.Schema}.{target_connection.TableName} integration execute operation started"

    def get_finish_log(self, data_integration_id: int, data_count: int):
        target_connection = self.data_integration_connection_service.get_target_connection(
            data_integration_id=data_integration_id)
        return f"{target_connection.Schema}.{target_connection.TableName} integration execute operation finished. (Source Data Count:{data_count})"

    def get_error_log(self, data_integration_id: int):
        target_connection = self.data_integration_connection_service.get_target_connection(
            data_integration_id=data_integration_id)
        return f"{target_connection.Schema}.{target_connection.TableName} integration execute operation getting error."

    def raise_error_check(self) -> bool:
        return True

    def execute_integration(self,
                            data_operation_job_execution_id: int,
                            data_operation_job_execution_integration_id: int,
                            data_operation_integration_id: int,
                            data_count: int) -> int:
        data_operation_integration = self.data_operation_integration_service.get_by_id(
            id=data_operation_integration_id)
        data_operation_integration_order = data_operation_integration.Order
        limit = data_operation_integration.Limit
        process_count = data_operation_integration.ProcessCount
        data_integration_code = data_operation_integration.DataIntegration.Code
        if limit != 0:
            if process_count > 1:
                self.sql_logger.info(
                    f"{data_operation_integration_order}-{data_integration_code} - operation will execute parallel. {process_count}-{limit}",
                    job_id=data_operation_job_execution_id)
                affected_row_count = self.execute_integration_process.start_parallel_process(
                    data_operation_job_execution_id=data_operation_job_execution_id,
                    data_operation_integration_id=data_operation_integration_id,
                    data_count=data_count)

            else:
                self.sql_logger.info(
                    f"{data_operation_integration_order}-{data_integration_code} - operation will execute serial. {limit}",
                    job_id=data_operation_job_execution_id)

                affected_row_count = self.execute_integration_process.start_serial_process(
                    data_operation_integration_id=data_operation_integration_id,
                    data_count=data_count)

        self.data_operation_job_execution_integration_service.create_event(
            data_operation_execution_integration_id=data_operation_job_execution_integration_id,
            event_code=EVENT_EXECUTION_INTEGRATION_EXECUTE_OPERATION, affected_row=data_count)
        return affected_row_count
