"""data_operation

Revision ID: 8ca2550ae4ac
Revises: ddc1c049a9f7
Create Date: 2020-12-19 20:40:22.373130

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8ca2550ae4ac'
down_revision = 'ddc1c049a9f7'
branch_labels = None
depends_on = None


def insert_connection_types():
    from models.dao.operation.DataOperationExecutionStatus import DataOperationExecutionStatus
    from models.dao.operation.DataOperationExecutionProcessStatus import DataOperationExecutionProcessStatus
    bind = op.get_bind()
    from sqlalchemy import orm
    session = orm.Session(bind=bind)
    data_operation_execution_status_list = [
        {
            "Id":1,
            "Name": "ExecutionInitialize",
            "Description": "ExecutionInitialize",
        },
        {
            "Id":2,
            "Name": "ExecutionStart",
            "Description": "ExecutionStart",
        },
        {
            "Id":3,
            "Name": "ExecutionFinish",
            "Description": "ExecutionFinish",
        },
    ]
    data_operation_execution_process_status_list = [
        {
            "Id":1,
            "Name": "ProcessInitialize",
            "Description": "ProcessInitialize",
        },
        {
            "Id":2,
            "Name": "ProcessStart",
            "Description": "ProcessStart",
        },
        {
            "Id":3,
            "Name": "ProcessFinish",
            "Description": "ProcessFinish",
        },
        {
            "Id":4,
            "Name": "DataReadStart",
            "Description": "DataReadStart",
        },
        {
            "Id":5,
            "Name": "DataReadEnd",
            "Description": "ProcessEnd",
        },
        {
            "Id":6,
            "Name": "DataWriteStart",
            "Description": "DataWriteStart",
        },
        {
            "Id":7,
            "Name": "DataWriteEnd",
            "Description": "DataWriteEnd",
        },
    ]
    data_operation_execution_statuses = []
    for data_operation_execution_status_json in data_operation_execution_status_list:
        data_operation_execution_status = DataOperationExecutionStatus(
            Name=data_operation_execution_status_json["Name"],
            Description=data_operation_execution_status_json["Description"]
        )
        data_operation_execution_statuses.append(data_operation_execution_status)
    session.bulk_save_objects(data_operation_execution_statuses)
    session.commit()
    data_operation_execution_process_statuses = []
    for data_operation_execution_process_status_json in data_operation_execution_process_status_list:
        data_operation_execution_process_status = DataOperationExecutionProcessStatus(
            Name=data_operation_execution_process_status_json["Name"],
            Description=data_operation_execution_process_status_json["Description"]
            )
        data_operation_execution_process_statuses.append(data_operation_execution_process_status)
    session.bulk_save_objects(data_operation_execution_process_statuses)
    session.commit()

def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute('CREATE SCHEMA "Operation"')
    op.create_table('DataOperation',
    sa.Column('Id', sa.Integer(), nullable=False),
    sa.Column('Name', sa.String(length=100), nullable=False),
    sa.Column('Limit', sa.Integer(), nullable=False),
    sa.Column('ProcessCount', sa.Integer(), nullable=False),
    sa.Column('CreatedByUserId', sa.Integer(), nullable=False),
    sa.Column('CreationDate', sa.DateTime(), nullable=False),
    sa.Column('LastUpdatedUserId', sa.Integer(), nullable=True),
    sa.Column('LastUpdatedDate', sa.DateTime(), nullable=True),
    sa.Column('IsDeleted', sa.Integer(), nullable=False),
    sa.Column('Comments', sa.String(length=1000), nullable=True),
    sa.Column('RowVersion', sa.TIMESTAMP(), nullable=True),
    sa.PrimaryKeyConstraint('Id'),
    schema='Operation'
    )
    op.create_table('DataOperationExecutionProcessStatus',
    sa.Column('Id', sa.Integer(), nullable=False),
    sa.Column('Name', sa.String(length=100), nullable=False),
    sa.Column('Description', sa.String(length=250), nullable=False),
    sa.Column('CreatedByUserId', sa.Integer(), nullable=False),
    sa.Column('CreationDate', sa.DateTime(), nullable=False),
    sa.Column('LastUpdatedUserId', sa.Integer(), nullable=True),
    sa.Column('LastUpdatedDate', sa.DateTime(), nullable=True),
    sa.Column('IsDeleted', sa.Integer(), nullable=False),
    sa.Column('Comments', sa.String(length=1000), nullable=True),
    sa.Column('RowVersion', sa.TIMESTAMP(), nullable=True),
    sa.PrimaryKeyConstraint('Id'),
    schema='Operation'
    )
    op.create_table('DataOperationExecutionStatus',
    sa.Column('Id', sa.Integer(), nullable=False),
    sa.Column('Name', sa.String(length=100), nullable=False),
    sa.Column('Description', sa.String(length=250), nullable=False),
    sa.Column('CreatedByUserId', sa.Integer(), nullable=False),
    sa.Column('CreationDate', sa.DateTime(), nullable=False),
    sa.Column('LastUpdatedUserId', sa.Integer(), nullable=True),
    sa.Column('LastUpdatedDate', sa.DateTime(), nullable=True),
    sa.Column('IsDeleted', sa.Integer(), nullable=False),
    sa.Column('Comments', sa.String(length=1000), nullable=True),
    sa.Column('RowVersion', sa.TIMESTAMP(), nullable=True),
    sa.PrimaryKeyConstraint('Id'),
    schema='Operation'
    )
    op.create_table('DataOperationExecution',
    sa.Column('Id', sa.Integer(), nullable=False),
    sa.Column('DataOperationId', sa.Integer(), nullable=True),
    sa.Column('ApSchedulerJobId', sa.Integer(), nullable=True),
    sa.Column('StatusId', sa.Integer(), nullable=True),
    sa.Column('StartDate', sa.DateTime(), nullable=False),
    sa.Column('EndDate', sa.DateTime(), nullable=True),
    sa.Column('CreatedByUserId', sa.Integer(), nullable=False),
    sa.Column('CreationDate', sa.DateTime(), nullable=False),
    sa.Column('LastUpdatedUserId', sa.Integer(), nullable=True),
    sa.Column('LastUpdatedDate', sa.DateTime(), nullable=True),
    sa.Column('IsDeleted', sa.Integer(), nullable=False),
    sa.Column('Comments', sa.String(length=1000), nullable=True),
    sa.Column('RowVersion', sa.TIMESTAMP(), nullable=True),
    sa.ForeignKeyConstraint(['ApSchedulerJobId'], ['Aps.ApSchedulerJob.Id'], ),
    sa.ForeignKeyConstraint(['DataOperationId'], ['Operation.DataOperation.Id'], ),
    sa.ForeignKeyConstraint(['StatusId'], ['Operation.DataOperationExecutionStatus.Id'], ),
    sa.PrimaryKeyConstraint('Id'),
    schema='Operation'
    )
    op.create_table('DataOperationIntegration',
    sa.Column('Id', sa.Integer(), nullable=False),
    sa.Column('DataOperationId', sa.Integer(), nullable=True),
    sa.Column('PythonDataIntegrationId', sa.Integer(), nullable=True),
    sa.Column('Order', sa.Integer(), nullable=False),
    sa.Column('SourceCount', sa.Integer(), nullable=True),
    sa.Column('CreatedByUserId', sa.Integer(), nullable=False),
    sa.Column('CreationDate', sa.DateTime(), nullable=False),
    sa.Column('LastUpdatedUserId', sa.Integer(), nullable=True),
    sa.Column('LastUpdatedDate', sa.DateTime(), nullable=True),
    sa.Column('IsDeleted', sa.Integer(), nullable=False),
    sa.Column('Comments', sa.String(length=1000), nullable=True),
    sa.Column('RowVersion', sa.TIMESTAMP(), nullable=True),
    sa.ForeignKeyConstraint(['DataOperationId'], ['Operation.DataOperation.Id'], ),
    sa.ForeignKeyConstraint(['PythonDataIntegrationId'], ['Integration.PythonDataIntegration.Id'], ),
    sa.PrimaryKeyConstraint('Id'),
    schema='Operation'
    )
    op.create_table('DataOperationSchedule',
    sa.Column('Id', sa.Integer(), nullable=False),
    sa.Column('DataOperationId', sa.Integer(), nullable=True),
    sa.Column('ApSchedulerJobId', sa.Integer(), nullable=True),
    sa.Column('StartDate', sa.DateTime(), nullable=False),
    sa.Column('EndDate', sa.DateTime(), nullable=True),
    sa.Column('Cron', sa.String(length=100), nullable=True),
    sa.Column('CreatedByUserId', sa.Integer(), nullable=False),
    sa.Column('CreationDate', sa.DateTime(), nullable=False),
    sa.Column('LastUpdatedUserId', sa.Integer(), nullable=True),
    sa.Column('LastUpdatedDate', sa.DateTime(), nullable=True),
    sa.Column('IsDeleted', sa.Integer(), nullable=False),
    sa.Column('Comments', sa.String(length=1000), nullable=True),
    sa.Column('RowVersion', sa.TIMESTAMP(), nullable=True),
    sa.ForeignKeyConstraint(['ApSchedulerJobId'], ['Aps.ApSchedulerJob.Id'], ),
    sa.ForeignKeyConstraint(['DataOperationId'], ['Operation.DataOperation.Id'], ),
    sa.PrimaryKeyConstraint('Id'),
    schema='Operation'
    )
    op.create_table('DataOperationExecutionProcess',
    sa.Column('Id', sa.Integer(), nullable=False),
    sa.Column('DataOperationExecutionId', sa.Integer(), nullable=True),
    sa.Column('StatusId', sa.Integer(), nullable=True),
    sa.Column('ProcessId', sa.Integer(), nullable=True),
    sa.Column('SubLimit', sa.Integer(), nullable=False),
    sa.Column('TopLimit', sa.Integer(), nullable=False),
    sa.Column('ElapsedTime', sa.Float(precision=2), nullable=True),
    sa.Column('CreatedByUserId', sa.Integer(), nullable=False),
    sa.Column('CreationDate', sa.DateTime(), nullable=False),
    sa.Column('LastUpdatedUserId', sa.Integer(), nullable=True),
    sa.Column('LastUpdatedDate', sa.DateTime(), nullable=True),
    sa.Column('IsDeleted', sa.Integer(), nullable=False),
    sa.Column('Comments', sa.String(length=1000), nullable=True),
    sa.Column('RowVersion', sa.TIMESTAMP(), nullable=True),
    sa.ForeignKeyConstraint(['DataOperationExecutionId'], ['Operation.DataOperationExecution.Id'], ),
    sa.ForeignKeyConstraint(['StatusId'], ['Operation.DataOperationExecutionProcessStatus.Id'], ),
    sa.PrimaryKeyConstraint('Id'),
    schema='Operation'
    )
    insert_connection_types()
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('DataOperationExecutionProcess', schema='Operation')
    op.drop_table('DataOperationSchedule', schema='Operation')
    op.drop_table('DataOperationIntegration', schema='Operation')
    op.drop_table('DataOperationExecution', schema='Operation')
    op.drop_table('DataOperationExecutionStatus', schema='Operation')
    op.drop_table('DataOperationExecutionProcessStatus', schema='Operation')
    op.drop_table('DataOperation', schema='Operation')
    # ### end Alembic commands ###
    op.execute('DROP SCHEMA "Operation"')
