import argparse
from typing import Any, Generator

from joblib import Parallel, delayed
from tqdm import tqdm

from src.account_helper import list_regions
from src.sg_helper import SgHelper


def main():
    parser = argparse.ArgumentParser(
        description="Delete unused security groups across AWS regions"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run in dry-run mode without actually deleting security groups",
    )
    parser.add_argument(
        "-t",
        "--threads",
        required=False,
        default=10,
        type=int,
        help="Number of threads to delete the unused security groups",
    )

    args = parser.parse_args()
    dry_run: bool = args.dry_run
    threads: int = int(args.threads)

    available_regions: list[str] = list_regions()
    total_sg_cleanedup = 0
    for each_region in available_regions:
        sg_helper: SgHelper = SgHelper(region=each_region, dry_run=dry_run)
        all_sg_list: list[str] = sg_helper.list_all_security_groups()
        all_unused_sgs: list[str] = sg_helper.filter_used_sgs(
            total_sg_groups=all_sg_list
        )
        if not all_unused_sgs:
            print(f"Skipping {each_region} as, no unused SGs identified")
            continue
        # total_sgs_deleted: int = sg_helper.delete_sg(sg_ids=all_unused_sgs)
        print(
            f"\nWorking on cleaning up: {each_region} region, {len(all_unused_sgs)} possible unused sgs"
        )

        total_sgs_deleted: Any = Parallel(n_jobs=threads, prefer="threads")(
            delayed(sg_helper.delete_sg)(sg_id) for sg_id in tqdm(all_unused_sgs)
        )
        number_of_deleted_sgs: int = 0
        for each_status in total_sgs_deleted:
            if each_status:
                number_of_deleted_sgs = number_of_deleted_sgs + 1

        if number_of_deleted_sgs > 0:
            print(
                f"completed deleting unused security groups, {number_of_deleted_sgs} sgs deleted on {each_region} region"
            )
        if dry_run:
            print(
                f"DRY RUN: {len(all_unused_sgs)} SGs might get deleted on {each_region} region"
            )
        total_sg_cleanedup = total_sg_cleanedup + number_of_deleted_sgs
    print(f"\nTotal Cleanup SGs: {total_sg_cleanedup}")


if __name__ == "__main__":
    main()
