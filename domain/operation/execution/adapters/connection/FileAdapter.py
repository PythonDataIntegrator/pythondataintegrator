import os
from queue import Queue
from threading import Thread
from typing import List

from injector import inject
import pandas as pd
from pandas import DataFrame

from domain.integration.services.DataIntegrationColumnService import DataIntegrationColumnService
from domain.integration.services.DataIntegrationConnectionService import DataIntegrationConnectionService
from infrastructor.IocManager import IocManager
from infrastructor.connection.adapters.ConnectionAdapter import ConnectionAdapter
from infrastructor.connection.file.FileProvider import FileProvider
from infrastructor.connection.models.DataQueueTask import DataQueueTask
from infrastructor.exceptions.NotSupportedFeatureException import NotSupportedFeatureException
from models.dto.PagingModifier import PagingModifier


class FileAdapter(ConnectionAdapter):
    @inject
    def __init__(self,
                 file_provider: FileProvider,
                 data_integration_connection_service: DataIntegrationConnectionService,
                 data_integration_column_service: DataIntegrationColumnService,
                 ):
        self.file_provider = file_provider
        self.data_integration_column_service = data_integration_column_service
        self.data_integration_connection_service = data_integration_connection_service

    def clear_data(self, data_integration_id) -> int:
        target_connection = self.data_integration_connection_service.get_target_connection(
            data_integration_id=data_integration_id)
        target_context = self.file_provider.get_context(
            connection=target_connection.Connection)
        data_integration_columns = self.data_integration_column_service.get_columns_by_integration_id(
            data_integration_id=data_integration_id)
        file_path = os.path.join(target_connection.File.Folder, target_connection.File.FileName)
        if target_connection.File.Csv.HasHeader:
            if target_connection.File.Csv.Header is not None and target_connection.File.Csv.Header != '':
                headers = target_connection.File.Csv.Header.split(target_connection.File.Csv.Separator)
            else:
                headers = [(data_integration_column.TargetColumnName) for data_integration_column in
                           data_integration_columns]
            truncate_affected_rowcount = target_context.recreate_file(
                file=file_path, headers=headers,
                separator=target_connection.File.Csv.Separator)
        else:
            truncate_affected_rowcount = target_context.delete_file(
                file=file_path)

        return truncate_affected_rowcount

    def get_source_data_count(self, data_integration_id) -> int:
        source_connection = self.data_integration_connection_service.get_source_connection(
            data_integration_id=data_integration_id)

        source_context = self.file_provider.get_context(connection=source_connection.Connection)
        file_path = os.path.join(source_connection.File.Folder, source_connection.File.FileName)
        data_count = source_context.get_data_count(file=file_path)
        if source_connection.File.Csv.HasHeader:
            data_count = data_count - 1
        return data_count

    @staticmethod
    def source_data_process(data_integration_id: int, limit: int, data_queue: Queue, result_queue: Queue):

        try:
            IocManager.initialize()
            data_integration_connection_service = IocManager.injector.get(DataIntegrationConnectionService)
            file_provider = IocManager.injector.get(FileProvider)

            source_connection = data_integration_connection_service.get_source_connection(
                data_integration_id=data_integration_id)

            source_context = file_provider.get_context(connection=source_connection.Connection)

            has_header = None
            if source_connection.File.Csv.HasHeader:
                has_header = 0
            headers = None
            separator = source_connection.File.Csv.Separator
            if source_connection.File.Csv.Header is not None and source_connection.File.Csv.Header != '':
                headers = source_connection.File.Csv.Header.split(separator)

            file_path = os.path.join(source_connection.File.Folder, source_connection.File.FileName)
            source_context.start_get_data(file=file_path,
                                          names=headers,
                                          header=has_header,
                                          limit=limit,
                                          separator=separator,
                                          data_queue=data_queue,
                                          result_queue=result_queue)
            data_queue_finish_task = DataQueueTask(IsFinished=True)
            data_queue.put(data_queue_finish_task)
        except Exception as ex:
            data_queue_error_task = DataQueueTask(IsFinished=True, Exception=ex)
            data_queue.put(data_queue_error_task)

    def start_source_data_process(self, data_integration_id: int, limit: int, data_queue: Queue, result_queue: Queue):
        main_t = Thread(target=FileAdapter.source_data_process,
                        args=(data_integration_id, limit, data_queue, result_queue,))
        main_t.start()

    def get_source_data(self, data_integration_id: int, paging_modifier: PagingModifier) -> DataFrame:
        source_connection = self.data_integration_connection_service.get_source_connection(
            data_integration_id=data_integration_id)
        source_context = self.file_provider.get_context(connection=source_connection.Connection)

        data_integration_columns = self.data_integration_column_service.get_columns_by_integration_id(
            data_integration_id=data_integration_id)
        has_header = None
        if source_connection.File.Csv.HasHeader:
            has_header = 0
        headers = None
        if source_connection.File.Csv.Header is not None and source_connection.File.Csv.Header != '':
            headers = source_connection.File.Csv.Header.split(source_connection.File.Csv.Separator)

        file_path = os.path.join(source_connection.File.Folder, source_connection.File.FileName)
        readed_data = source_context.get_data(file=file_path,
                                              names=headers,
                                              header=has_header,
                                              start=paging_modifier.Start,
                                              limit=paging_modifier.Limit,
                                              separator=source_connection.File.Csv.Separator)
        column_names = [(data_integration_column.SourceColumnName) for data_integration_column in
                        data_integration_columns]
        data = readed_data[column_names]
        replaced_data = data.where(pd.notnull(data), None)
        return replaced_data.values.tolist()

    def prepare_data(self, data_integration_id: int, source_data: List[any]) -> List[any]:
        target_connection = self.data_integration_connection_service.get_target_connection(
            data_integration_id=data_integration_id)

        target_context = self.file_provider.get_context(connection=target_connection.Connection)

        data_integration_columns = self.data_integration_column_service.get_columns_by_integration_id(
            data_integration_id=data_integration_id)

        column_rows = [(data_integration_column.ResourceType, data_integration_column.SourceColumnName,
                        data_integration_column.TargetColumnName) for data_integration_column in
                       data_integration_columns]
        prepared_data = target_context.prepare_insert_row(data=source_data, column_rows=column_rows)
        return prepared_data

    def write_target_data(self, data_integration_id: int, prepared_data: List[any], ) -> int:
        target_connection = self.data_integration_connection_service.get_target_connection(
            data_integration_id=data_integration_id)

        target_context = self.file_provider.get_context(connection=target_connection.Connection)
        df = pd.DataFrame(prepared_data)
        data = df.where(pd.notnull(df), None)
        file_path = os.path.join(target_connection.File.Folder, target_connection.File.FileName)
        affected_row_count = target_context.write_to_file(file=file_path,
                                                          data=data,
                                                          separator=target_connection.File.Csv.Separator)
        return affected_row_count

    def do_target_operation(self, data_integration_id: int) -> int:
        raise NotSupportedFeatureException("File Target Operation")
