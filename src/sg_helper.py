import boto3


class SgHelper:
    def __init__(self, region: str, dry_run: bool) -> None:
        self.region = region
        self.ec2_client = boto3.client("ec2", region_name=region)
        self.dry_run = dry_run

    def list_all_security_groups(self) -> list[str]:
        sg_ids = []
        try:
            paginator = self.ec2_client.get_paginator("describe_security_groups")
            response_iterator = paginator.paginate()
            for response in response_iterator:
                for each_sg in response["SecurityGroups"]:
                    sg_id = each_sg["GroupId"]
                    sg_name: str = each_sg["GroupName"]
                    if sg_name == "default":
                        continue
                    sg_ids.append(sg_id)
        except Exception as e:
            print(
                f"error occurred while listing all security groups, region: {self.region}"
            )
            print(str(e))
        return sg_ids

    def filter_used_sgs(self, total_sg_groups: list[str]) -> list[str]:
        unused_sgs: set[str] = set()
        all_used_sgs = self.__get_all_attached_sgs()
        for each_sg_id in total_sg_groups:
            if each_sg_id not in all_used_sgs:
                unused_sgs.add(each_sg_id)
        return list(unused_sgs)

    def __get_all_attached_sgs(self) -> set[str]:
        output: set[str] = set()
        try:
            paginator = self.ec2_client.get_paginator("describe_network_interfaces")
            response_iterator = paginator.paginate()
            for response in response_iterator:
                for each_network_interfaces in response["NetworkInterfaces"]:
                    for all_attached_groups in each_network_interfaces["Groups"]:
                        group_id = all_attached_groups["GroupId"]
                        output.add(group_id)
        except Exception as e:
            print(
                f"error occurred while listing all attached security groups, region: {self.region}"
            )
            print(str(e))
        return output

    def delete_sg(self, sg_id: str) -> bool:
        total_sgs_deleted = 0
        try:
            response = self.ec2_client.delete_security_group(
                GroupId=sg_id, DryRun=self.dry_run
            )
            total_sgs_deleted = total_sgs_deleted + 1

        except Exception as e:
            if "DryRun flag is set" in str(e):
                return False
            if 'name: "default" cannot be deleted by a user' in str(e):
                return False

            if "has a dependent object" in str(e):
                return False

            print(
                f"error occurred while trying delete sg {sg_id}, region: {self.region}"
            )
            print(str(e))
        return True
