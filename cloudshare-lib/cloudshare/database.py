"""
MetadataManager: OOP wrapper for Amazon DynamoDB operations.

Provides CRUD operations for a single DynamoDB table using
a composite primary key (partition key + sort key).
"""

import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
from typing import Optional


class MetadataManager:
    """Manages metadata persistence using Amazon DynamoDB.

    Uses a single DynamoDB table with a composite key:
    - Partition key (pk_name): e.g. 'user_id' or 'recipient_email'
    - Sort key (sk_name): e.g. 'file_id' or 'notification_id'

    Attributes:
        table_name (str): The DynamoDB table name.
        pk_name (str): Partition key attribute name.
        sk_name (str): Sort key attribute name.
        table: The boto3 DynamoDB Table resource.
    """

    def __init__(
        self,
        table_name: str,
        pk_name: str = "user_id",
        sk_name: str = "file_id",
        region: str = "us-east-1",
    ):
        """Initialise the MetadataManager.

        Args:
            table_name: DynamoDB table name.
            pk_name: Partition key attribute name.
            sk_name: Sort key attribute name.
            region: AWS region string.
        """
        self.table_name = table_name
        self.pk_name = pk_name
        self.sk_name = sk_name
        # boto3 picks up credentials from the EC2 IAM role automatically
        dynamodb = boto3.resource("dynamodb", region_name=region)
        self.table = dynamodb.Table(table_name)

    def put_item(self, item: dict) -> dict:
        """Write an item to the DynamoDB table.

        Args:
            item: Dictionary representing the full item to store.
                  Must include the pk_name and sk_name attributes.

        Returns:
            The item that was stored.

        Raises:
            ClientError: If the DynamoDB put operation fails.
        """
        self.table.put_item(Item=item)
        return item

    def get_item(self, pk_value: str, sk_value: str) -> Optional[dict]:
        """Retrieve a single item by its primary key.

        Args:
            pk_value: Value of the partition key.
            sk_value: Value of the sort key.

        Returns:
            The item dict, or None if not found.
        """
        response = self.table.get_item(
            Key={self.pk_name: pk_value, self.sk_name: sk_value}
        )
        return response.get("Item")

    def query_items(self, pk_value: str) -> list:
        """Query all items for a given partition key.

        Args:
            pk_value: Value of the partition key to query on.

        Returns:
            List of item dicts matching the partition key.
        """
        response = self.table.query(
            KeyConditionExpression=Key(self.pk_name).eq(pk_value)
        )
        return response.get("Items", [])

    def update_item(self, pk_value: str, sk_value: str, updates: dict) -> dict:
        """Update specific attributes of an existing item.

        Args:
            pk_value: Value of the partition key.
            sk_value: Value of the sort key.
            updates: Dict of attribute names to new values.

        Returns:
            The updated item attributes.

        Raises:
            ClientError: If the DynamoDB update fails.
        """
        # Build the update expression dynamically from the updates dict
        update_expr = "SET " + ", ".join(f"#attr_{i} = :val_{i}" for i in range(len(updates)))
        expr_names = {f"#attr_{i}": k for i, k in enumerate(updates.keys())}
        expr_values = {f":val_{i}": v for i, v in enumerate(updates.values())}

        response = self.table.update_item(
            Key={self.pk_name: pk_value, self.sk_name: sk_value},
            UpdateExpression=update_expr,
            ExpressionAttributeNames=expr_names,
            ExpressionAttributeValues=expr_values,
            ReturnValues="ALL_NEW",
        )
        return response.get("Attributes", {})

    def delete_item(self, pk_value: str, sk_value: str) -> bool:
        """Delete an item from the table.

        Args:
            pk_value: Value of the partition key.
            sk_value: Value of the sort key.

        Returns:
            True if deletion succeeded, False otherwise.
        """
        try:
            self.table.delete_item(
                Key={self.pk_name: pk_value, self.sk_name: sk_value}
            )
            return True
        except ClientError:
            return False
