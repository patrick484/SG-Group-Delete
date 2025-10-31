import boto3
import json
from botocore.exceptions import ClientError

INITIAL_REGION = "us-east-1"
DRY_RUN_MODE = False  # Set to False to perform actual deletion

def get_all_enabled_regions():
    """Fetches a list of all enabled AWS regions."""
    try:
        ec2_client = boto3.client("ec2", region_name=INITIAL_REGION)
        return [r["RegionName"] for r in ec2_client.describe_regions(AllRegions=False)["Regions"]]
    except ClientError as e:
        # Fails silently and returns None if credentials/permissions are invalid
        return None

def analyze_and_process_security_groups(region, dry_run_mode):

    region_client = boto3.client("ec2", region_name=region)
    
    
    try:
        # 1. Get ALL SG IDs and details
        sg_response = region_client.describe_security_groups()
        all_sg_details = [(sg["GroupId"], sg["GroupName"], sg["VpcId"]) 
                          for sg in sg_response.get("SecurityGroups", [])]

        # 2. Get USED SG IDs (from ENIs)
        eni_response = region_client.describe_network_interfaces()
        used_sg_ids = {group["GroupId"] 
                       for eni in eni_response.get("NetworkInterfaces", []) 
                       for group in eni.get("Groups", [])}
        
        # 3. Process and Delete
        for sg_id, sg_name, vpc_id in all_sg_details:
            # Check for unused and skip default SG
            if sg_id not in used_sg_ids and sg_name != "default":
                
                try:
                    # Attempt the deletion (or Dry Run)
                    region_client.delete_security_group(GroupId=sg_id, DryRun=dry_run_mode)

                    action = "SIMULATED DELETED" if dry_run_mode else "**DELETED**"
                    
                    # Single-line successful output
                    print(f"✅ {region}: {sg_id} ({sg_name}) {action}.")

                except ClientError as delete_e:
                    error_code = delete_e.response["Error"]["Code"]
                    
                    # Single-line failure output
                    print(f"❌ {region}: {sg_id} ({sg_name}) FAILED. Reason: {error_code}.")

    except ClientError as e:
        error_str = str(e)
        if "AccessDenied" in error_str or "is not enabled for this account" in error_str:
            print(f"⚠️ {region}: Skipping due to Access Denied or Region Not Enabled.")
        else:
            print(f"❌ {region}: Unexpected error: {e}")


def main():
    """Main function to orchestrate the security group cleanup workflow."""
    
    all_regions = get_all_enabled_regions()
    if not all_regions:
        return

    # Removed the initial print statements as requested

    # Iterate and process each region
    for region in all_regions:
        # Removed the per-region print statement
        analyze_and_process_security_groups(region, DRY_RUN_MODE)

    # Removed the final summary report printing as requested

if __name__ == "__main__":
    main()