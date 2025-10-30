import boto3
import json
import csv
from botocore.exceptions import ClientError

# --- CONFIGURATION ---
# <<< CHANGE >>> Set an initial region for the first API call (bypasses NoRegionError)
INITIAL_REGION = 'us-east-1' 

# <<< CHANGE >>> SAFETY TOGGLE: 
# Set to True to ONLY test the deletion without actually deleting.
# Set to False to perform the actual deletion.
DRY_RUN_MODE = False
# ---------------------

def find_unused_security_groups():

    # Initialize EC2 client with an initial region to list all regions
    # <<< CHANGE >>> Added region_name=INITIAL_REGION to fix NoRegionError
    ec2_client = boto3.client("ec2", region_name=INITIAL_REGION)


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
    # <<< CHANGE >>> List to track SGs that failed deletion (e.g., due to being referenced)
    failed_to_delete = [] 

    print(
        f"Starting audit for unused security groups across {len(all_regions)} regions..."
    )
    # <<< CHANGE >>> Print Dry Run status clearly
    print(f"*** DRY RUN MODE IS {'ON' if DRY_RUN_MODE else 'OFF'} ***")
    print("-" * 50)

    # 1. Iterate through each region
    for region in all_regions:
        print(f"\n  🔍 Region: {region}")
        try:
            region_client = boto3.client("ec2", region_name=region)

            # --- Get ALL Security Group IDs ---
            sg_response = region_client.describe_security_groups()
            all_sg_ids = set()
            for sg in sg_response.get("SecurityGroups", []):
                all_sg_ids.add((sg["GroupId"], sg["GroupName"], sg["VpcId"]))

            # --- Get USED Security Group IDs (referenced by ENIs) ---
            eni_response = region_client.describe_network_interfaces()
            used_sg_ids = set()

            for eni in eni_response.get("NetworkInterfaces", []):
                for group in eni.get("Groups", []):
                    used_sg_ids.add(group["GroupId"])

            # --- Determine Unused Security Groups & Attempt Deletion ---
            current_region_processed_count = 0

            for sg_id, sg_name, vpc_id in all_sg_ids:
                if sg_id not in used_sg_ids:
                    
                    # Filter out the default SG (sg-xxxx) which often appears unused but cannot be deleted
                    if sg_name != "default":
                        
                        try:
                            # <<< CHANGE >>> Attempt the deletion (or Dry Run)
                            response = region_client.delete_security_group(
                                GroupId=sg_id,
                                DryRun=DRY_RUN_MODE 
                            )

                            action = "SIMULATED DELETION" if DRY_RUN_MODE else "DELETED"
                            print(f"    ✅ {action}: {sg_id} ({sg_name})")
                            
                            status = "DRY_RUN_SUCCESS (Ready for deletion)" if DRY_RUN_MODE else "DELETED"

                            # Append successful action to the report
                            unused_sg_report.append(
                                {
                                    "Region": region,
                                    "SecurityGroupId": sg_id,
                                    "SecurityGroupName": sg_name,
                                    "VpcId": vpc_id,
                                    "Status": status,
                                }
                            )
                            current_region_processed_count += 1
                            

                        except ClientError as delete_e:
                            # Handle specific deletion failure errors (e.g., referenced by another SG)
                            error_code = delete_e.response['Error']['Code']
                            error_msg = delete_e.response['Error']['Message']
                            
                            print(f"    ❌ FAILED: {sg_id} Reason: {error_code}")
                            
                            # Add the failed SG to the dedicated failure report list
                            failed_to_delete.append({
                                "Region": region,
                                "SecurityGroupId": sg_id,
                                "SecurityGroupName": sg_name,
                                "VpcId": vpc_id,
                                "Status": f"FAILED: {error_code}",
                                "Reason": error_msg
                            })
                            
                            # Also include the failure in the main report
                            unused_sg_report.append(
                                {
                                    "Region": region,
                                    "SecurityGroupId": sg_id,
                                    "SecurityGroupName": sg_name,
                                    "VpcId": vpc_id,
                                    "Status": f"FAILED: {error_code}",
                                }
                            )
                            current_region_processed_count += 1 # Count it as processed but failed


            print(f"  Summary: {current_region_processed_count} SGs {'processed' if DRY_RUN_MODE else 'deleted'} in {region}.")

        except ClientError as e:
            if "AccessDenied" in str(e) or "is not enabled for this account" in str(e):
                print(f"  ⚠️ Skipping {region}: Access Denied or Region Not Enabled.")
            else:
                print(f"  ❌ An unexpected error occurred in {region}: {e}")

    # 2. Compile and display the final report
    if unused_sg_report:
        print("\n" + "="*80)
        print("✨ FINAL RUN REPORT ✨")
        print(f"*** DRY RUN MODE WAS {'ON' if DRY_RUN_MODE else 'OFF'} ***")
        print("="*80)
        
        print("\n\n--- MAIN RESULTS (JSON Output) ---")
        # Output all processed SGs, including those that failed
        print(json.dumps(unused_sg_report, indent=4))
        
        if failed_to_delete:
            print("\n\n--- FAILED DELETIONS SUMMARY ---")
            print("These groups are typically referenced by other SGs, ENIs not found by describe-network-interfaces, or resources in a pending state.")
            print(json.dumps(failed_to_delete, indent=4))
        
    else:
        print("\n🎉 No unused security groups found across all checked regions.")


if __name__ == "__main__":
    find_unused_security_groups()