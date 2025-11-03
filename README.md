# AWS Security Group Cleanup Tool

A Python tool to automatically identify and delete unused AWS Security Groups across all enabled regions in your AWS account. This tool helps maintain a clean and secure AWS environment by removing orphaned security groups that are no longer attached to any network interfaces.

## Prerequisites

- Python 3.8 or higher
- AWS CLI configured with appropriate credentials
- AWS IAM permissions for:
  - `account:ListRegions`
  - `ec2:DescribeSecurityGroups`
  - `ec2:DescribeNetworkInterfaces`
  - `ec2:DeleteSecurityGroup`

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd SG
```

2. Create and activate a virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

**Always start with a dry run to see what would be deleted:**
```bash
python main.py --dry-run
```

**Delete unused security groups:**
```bash
python main.py
```

**Use custom number of threads:**
```bash
python main.py --threads 5
```

### Command Line Options

```
usage: main.py [-h] [--dry-run] [-t THREADS]

Delete unused security groups across AWS regions

options:
  -h, --help            show this help message and exit
  --dry-run             Run in dry-run mode without actually deleting security groups
  -t, --threads THREADS
                        Number of threads to delete the unused security groups (default: 10)
```

