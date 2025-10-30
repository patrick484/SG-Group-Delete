import boto3
import pandas as pd
from botocore.exceptions import ClientError

def find_unused_security_groups():

    # Initialize EC2 client in a default region to get the list of all regions
    ec2_client = boto3.client("ec2")


    try:
        # Get all enabled regions for the account
        response = ec2_client.describe_regions(AllRegions=False)
        all_regions = [region["RegionName"] for region in response["Regions"]]
    except ClientError as e:
        print(
            f"❌ Error describing regions. Check your credentials and permissions: {e}"
        )
        return

    unused_sg_report = []

    print(
        f"Starting audit for unused security groups across {len(all_regions)} regions..."
    )
    print("-" * 50)

    # 1. Iterate through each region
    for region in all_regions:
        try:
            region_client = boto3.client("ec2", region_name=region)

            # --- Get ALL Security Group IDs ---
            sg_response = region_client.describe_security_groups()
            all_sg_ids = set()
            for sg in sg_response.get("SecurityGroups", []):
                # The 'default' security group cannot be deleted, so we typically skip it.
                # However, it will still appear in the 'unused' list if no resources use it.
                all_sg_ids.add((sg["GroupId"], sg["GroupName"], sg["VpcId"]))

            # --- Get USED Security Group IDs (referenced by ENIs) ---
            eni_response = region_client.describe_network_interfaces()
            used_sg_ids = set()

            for eni in eni_response.get("NetworkInterfaces", []):
                for group in eni.get("Groups", []):
                    # We only care about the GroupId here to build the 'used' set
                    used_sg_ids.add(group["GroupId"])

            # --- Determine Unused Security Groups ---

            current_region_unused_count = 0

            for sg_id, sg_name, vpc_id in all_sg_ids:
                if sg_id not in used_sg_ids:
                    # Filter out the default SG (sg-xxxx) which often appears unused but cannot be deleted

                    if sg_name != "default":
                        unused_sg_report.append(
                            {
                                "Region": region,
                                "SecurityGroupId": sg_id,
                                "SecurityGroupName": sg_name,
                                "VpcId": vpc_id,
                                "Status": "UNUSED (No ENI Attachment)",
                            }
                        )
                        current_region_unused_count += 1

            print(
                f"  ✅ {region}: Found {current_region_unused_count} potentially unused security groups."
            )

        except ClientError as e:
            if "AccessDenied" in str(e) or "is not enabled for this account" in str(e):
                print(f"  ⚠️ Skipping {region}: Access Denied or Region Not Enabled.")
            else:
                print(f"  ❌ An unexpected error occurred in {region}: {e}")

    # 2. Compile and display the final report
    if unused_sg_report:
        df = pd.DataFrame(unused_sg_report)

        print("\n" + "=" * 80)
        print("🔍 Final Report: Unused Security Groups Across All Regions")
        print("=" * 80)
        print(df.to_markdown(index=False))

        # Optional: Save to CSV
        report_filename = "unused_security_groups_report.csv"
        df.to_csv(report_filename, index=False)
        print(f"\nReport saved to: **{report_filename}**")
    else:
        print("\n🎉 No unused security groups found across all checked regions.")


if __name__ == "__main__":
    find_unused_security_groups()
