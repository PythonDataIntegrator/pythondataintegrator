import json
import os
from unittest import TestCase

from infrastructor.IocManager import IocManager
from tests.integrationtests.common.TestManager import TestManager


class TestConnectorTypeResuource(TestCase):

    def __init__(self, methodName='TestConnectorTypeResuource'):
        super(TestConnectorTypeResuource, self).__init__(methodName)
        self.test_manager = TestManager()

    def print_error_detail(self, data):
        print(data['message'] if 'message' in data else '')
        print(data['traceback'] if 'traceback' in data else '')
        print(data['message'] if 'message' in data else '')

    def test_get_connector_type(self):
        response_data = self.test_manager.api_client.get('/api/Connection/ConnectorType')
        assert response_data['IsSuccess'] == True
