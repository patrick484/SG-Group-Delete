import boto3
import botocore


def list_regions() -> list[str]:
    DEFAULT_REGION_LIST = [
        "ap-northeast-1",  # Asia Pacific (Tokyo)
        "ap-south-1",  # Asia Pacific (Mumbai)
        "ap-southeast-1",  # Asia Pacific (Singapore)
        "ap-southeast-2",  # Asia Pacific (Sydney)
        "ca-central-1",  # Canada (Central)
        "eu-central-1",  # Europe (Frankfurt)
        "eu-north-1",  # Europe (Stockholm)
        "eu-west-1",  # Europe (Ireland)
        "eu-west-2",  # Europe (London)
        "eu-west-3",  # Europe (Paris)
        "sa-east-1",  # South America (São Paulo)
        "us-east-1",  # US East (N. Virginia)
        "us-east-2",  # US East (Ohio)
        "us-west-1",  # US West (N. California)
        "us-west-2",  # US West (Oregon)
    ]
    output: list[str] = []
    try:
        client = boto3.client("account")
        paginator = client.get_paginator("list_regions")

        response_iterator = paginator.paginate(
            RegionOptStatusContains=["ENABLED", "ENABLING", "ENABLED_BY_DEFAULT"]
        )
        for response in response_iterator:
            for region_data in response["Regions"]:
                output.append(region_data["RegionName"])
    except botocore.exceptions.ClientError as e:
        error_code = e.response["Error"]["Code"]
        if error_code == "AccessDeniedException":
            print(
                f"error occurred while listing all active regions !!!, Using default regions list."
            )
            print(str(e))
            output = DEFAULT_REGION_LIST
        else:
            raise e
    return output
