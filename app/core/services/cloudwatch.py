import boto3
from botocore.exceptions import ClientError
import os
from pathlib import Path
from app.core.exceptions import ErrorCode
from app.core.services.base import LogService


class CloudWatchService(LogService):
    def __init__(self, is_local="development", region_name="us-east-1", log_group_name="my-log-group",
                 log_stream_name="my-log-stream", s3_client=None):
        """
        Initializes the CloudWatch service.
        If is_local=True, it will simulate the logging locally instead of AWS CloudWatch.
        """
        self.is_local = is_local == "development"
        self.region_name = region_name
        self.log_group_name = log_group_name
        self.log_stream_name = log_stream_name
        self.client = s3_client

        if not self.is_local:
            self.client = boto3.client("logs", region_name=self.region_name)
            self.create_log_group_if_not_exists()
            self.create_log_stream_if_not_exists()

    def create_log_group_if_not_exists(self):
        """Ensure the CloudWatch log group exists."""
        try:
            self.client.describe_log_groups(logGroupNamePrefix=self.log_group_name)
        except ClientError as e:
            if e.response["Error"]["Code"] == "ResourceNotFoundException":
                self.client.create_log_group(logGroupName=self.log_group_name)

    def create_log_stream_if_not_exists(self):
        """Ensure the CloudWatch log stream exists."""
        try:
            self.client.describe_log_streams(logGroupName=self.log_group_name, logStreamNamePrefix=self.log_stream_name)
        except ClientError as e:
            if e.response["Error"]["Code"] == "ResourceNotFoundException":
                self.client.create_log_stream(
                    logGroupName=self.log_group_name,
                    logStreamName=self.log_stream_name
                )

    def log(self, message: str):
        """Log a message to AWS CloudWatch."""
        if self.is_local:
            # If running locally, log to a file (simulating CloudWatch logs)
            self.log_locally(message)
        else:
            # Send the log message to CloudWatch
            try:
                response = self.client.put_log_events(
                    logGroupName=self.log_group_name,
                    logStreamName=self.log_stream_name,
                    logEvents=[{
                        "timestamp": int(round(os.times()[4] * 1000)),  # Current time in ms
                        "message": message
                    }]
                )
                print(f"Successfully logged to CloudWatch: {response}")
            except ClientError as e:
                raise ErrorCode.BadRequest(f"Error logging to CloudWatch: {e.response['Error']['Message']}")

    def log_locally(self, message: str):
        """Simulate logging to local storage (for testing purposes)."""
        log_path = Path("local_logs") / f"{self.log_group_name}.log"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(log_path, "a") as log_file:
            log_file.write(f"{message}\n")
        print(f"Logged locally: {message}")
