# 


`python3 -m venv .venv`
`source .venv/bin/activate`
`pip install -r requirements.txt`

### Usage
```
usage: main.py [-h] [--dry-run] [-t THREADS]

Delete unused security groups across AWS regions

options:
  -h, --help            show this help message and exit
  --dry-run             Run in dry-run mode without actually deleting security groups
  -t, --threads THREADS
                        Number of threads to delete the unused security groups
```

