"""
    services/resource.py
    Resource management for API
"""


TABLES = {
    'author': {
        'table_name': 'author-table-dev',
        'primary_key': 'authorId'
    },
    'post': {
        'table_name': 'post-table-dev',
        'primary_key': 'postId'
    },
    'media': {
        'table_name': 'media-table-dev',
        'primary_key': 'mediaId'
    }
}

BUCKETS = {
    'media': {
        'bucket_name': 'media-bucket-dev',
        'parent_key': 'media/'
    }
}


def create_table(client, table, logger):
    """Create dynamodb tables"""
    new_table = client.create_table(
        TableName=f"{table['table_name']}",
        KeySchema=[
            {
                'AttributeName': f"{table['primary_key']}",
                'KeyType': 'HASH'
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': f"{table['primary_key']}",
                'AttributeType': 'S'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 10,
            'WriteCapacityUnits': 10
        }
    )
    logger.info(
        f"$[{table['table_name']}] \u279C $w[{new_table.table_status}]")
    return new_table


def create_bucket(client, resource, bucket, logger):
    """create s3 bucket resource"""
    logger.info(f'Creating Bucket: $[{bucket["bucket_name"]}]')
    _bucket = client.create_bucket(
        Bucket=bucket['bucket_name'], ACL='public-read')
    new_bucket = resource.Bucket(bucket['bucket_name'])
    logger.info(f"$[{bucket['bucket_name']}] \u279C $w[ACTIVE]")
    return new_bucket
