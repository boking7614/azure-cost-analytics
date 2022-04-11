# Document
# https://docs.microsoft.com/zh-tw/python/api/azure-mgmt-costmanagement/azure.mgmt.costmanagement?view=azure-python

import os
import logging
import time
from datetime import datetime , timedelta
from dotenv import load_dotenv
from influxdb import InfluxDBClient

from azure.identity import ClientSecretCredential
from azure.mgmt.costmanagement import CostManagementClient

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

load_dotenv()

subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"]
tenant_id = os.environ["AZURE_TENANT_ID"]
client_id = os.environ["AZURE_CLIENT_ID"]
client_secret = os.environ["AZURE_CLIENT_SECRET"]

def az_authentication():
    credential = ClientSecretCredential(tenant_id=tenant_id, client_id=client_id, client_secret=client_secret)
    return credential

def request_cost(from_ts, to_ts):
    cost_client = CostManagementClient(az_authentication())

    parameters = {
        'type': 'ActualCost',
        'timeframe': 'Custom',
        'time_period': {
            'from_property': from_ts,
            'to': to_ts
        },
        'dataset': {
            'aggregation': {
                'totalCost': {
                    'name': 'Cost',
                    'function':'Sum'
                }
            },
            'granularity': 'Daily', 
            'grouping': [
                {'type':'Dimension', 'name': 'ResourceId'},
                {'type':'Dimension', 'name': 'ResourceType'},
                {'type':'Dimension', 'name': 'ResourceGroup'}
            ]
        }
    }

    results = cost_client.query.usage(scope=f"/subscriptions/{subscription_id}/", parameters = parameters)
    return results.rows

def main():
    client = InfluxDBClient('152.70.96.186', 8086, 'ocidb_user', 'Sysageisgood-888','cloud_cost')
    logger.info("Start request.")
    data = []
    for item in request_cost(from_ts,to_ts):
        data.append(
            {
                "measurement": "azure",
                "tags": {
                        "company": "sysagecloud",
                        "resource_type": item[3],
                        "resource_name": item[2].split("/")[-1],
                        "resource_group": item[4]
                    },
                    "fields":{
                        "cost": item[0]
                    },
                    "time": f'{str(item[1])[0:4]}-{str(item[1])[4:6]}-{str(item[1])[6:8]}T00:00:00'
            }
        )
    logger.info("Start update data.")
    client.write_points(data)



if __name__ == "__main__":
    start_time = time.time()
    # from_ts = '2022-03-22T00:00:00+08:00'
    # to_ts = '2022-04-06T23:59:59+08:00'
    from_ts = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%dT00:00:00+00:00")
    to_ts = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%dT23:59:59+00:00")
    main()
    # total = 0
    # for item in request_cost(from_ts, to_ts):
    #     total += item[0]
    # print(total)
    process_time = time.time() - start_time
    logger.info(f"Processing completed {process_time:.3f} seconds")
