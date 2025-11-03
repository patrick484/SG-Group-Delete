# AWS Security Group Cleanup Tool

A Python tool to automatically identify and delete unused AWS Security Groups across all enabled regions in your AWS account. This tool helps maintain a clean and secure AWS environment by removing orphaned security groups that are no longer attached to any network interfaces.

## Features

- 🌐 **Multi-region support**: Scans all enabled AWS regions in your account
- 🔍 **Smart detection**: Identifies unused security groups by checking network interface attachments
- 🧵 **Parallel processing**: Uses multithreading for efficient deletion across regions
- 🛡️ **Safe operations**: 
  - Dry-run mode for testing before actual deletion
  - Automatically skips default security groups
  - Handles dependent object errors gracefully
- 📊 **Progress tracking**: Real-time progress bars and detailed reporting

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

## How It Works

1. **Region Discovery**: Queries AWS Account API to get all enabled regions
2. **Security Group Enumeration**: Lists all security groups in each region (excludes default SGs)
3. **Usage Detection**: Checks all network interfaces to identify which security groups are actually in use
4. **Cleanup**: Deletes unused security groups in parallel across all regions

## Safety Features

- **Dry Run Mode**: Test the tool safely without making any changes
- **Default SG Protection**: Never attempts to delete default security groups
- **Dependency Handling**: Gracefully handles security groups that have dependent objects
- **Error Recovery**: Continues processing other security groups even if some deletions fail

## Example Output

```
Working on cleaning up: us-east-1 region, 5 possible unused sgs
100%|████████████████| 5/5 [00:02<00:00,  2.31it/s]
completed deleting unused security groups, 5 sgs deleted on us-east-1 region

Skipping us-west-1 as, no unused SGs identified

Working on cleaning up: eu-west-1 region, 3 possible unused sgs
100%|████████████████| 3/3 [00:01<00:00,  2.85it/s]
completed deleting unused security groups, 3 sgs deleted on eu-west-1 region

Total Cleanup SGs: 8
```

## Project Structure

```
SG/
├── main.py                 # Main application entry point
├── requirements.txt        # Python dependencies
├── src/
│   ├── account_helper.py   # AWS account and region management
│   └── sg_helper.py        # Security group operations
└── README.md              # This file
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This tool modifies your AWS infrastructure by deleting security groups. Always use the `--dry-run` option first to review what would be deleted. The authors are not responsible for any unintended deletions or service disruptions.

