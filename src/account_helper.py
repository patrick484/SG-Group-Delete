import boto3


def list_regions() -> list[str]:
    output: list[str] = []
    client = boto3.client("account")
    paginator = client.get_paginator("list_regions")

    response_iterator = paginator.paginate(
        RegionOptStatusContains=["ENABLED", "ENABLING", "ENABLED_BY_DEFAULT"]
    )
    for response in response_iterator:
        for region_data in response["Regions"]:
            output.append(region_data["RegionName"])
    return output
