# -*- coding: utf-8 -*-

"""The script generates monthly cost report for AWS account
"""

import datetime
import pandas

import boto3

__author__ = 'Oleksandr Babichuk'
__email__ = 'Oleksandr.Babichuk@gmail.com'


def main():
    """
    main function
    """
    timestamp = datetime.datetime.utcnow()
    start_day = timestamp.replace(day=1).strftime('%Y-%m-%d')
    end_day = timestamp.strftime('%Y-%m-%d')

    client = boto3.client('ce')
    response = client.get_cost_and_usage(
        TimePeriod={
            'Start': start_day,
            'End': end_day
        },
        # Available options: MONTHLY, DAILY, or HOURLY
        Granularity='MONTHLY',
        Metrics=['UnblendedCost'],
        GroupBy=[
            {
                'Type': 'DIMENSION',
                'Key': 'LINKED_ACCOUNT'
            },
            {
                'Type': 'DIMENSION',
                'Key': 'SERVICE'
            }
        ]
    )

    billing_section = response['ResultsByTime'][0]['Groups']

    unformed_df = pandas.DataFrame.from_dict(billing_section)

    billing_df = pandas.DataFrame(
        (i[-1] for i in unformed_df['Keys']),
        columns=['Billing Unit']
    )

    metrics_df = pandas.DataFrame(
        (
            unformed_df['Metrics'][i][j]
            for i in unformed_df['Metrics'].keys()
            for j in unformed_df['Metrics'][i].keys()
        )
    )
    # Rename columns
    metrics_df.columns = ['Amount', 'Currency']

    receipt_df = pandas.concat([billing_df, metrics_df], axis=1)

    print(receipt_df.to_string(index=False))


if __name__ == '__main__':
    main()
