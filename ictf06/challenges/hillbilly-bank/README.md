# iCTF 2006 — HillBilly Bank

**Edition:** iCTF 2006
**Category:** crypto
**Language:** Python 2

## Description

The Hillbilly Bank is a fictional rural financial institution with an
RSA-based check signing system. Teams attacked and defended the bank's
infrastructure.

### Architecture

The bank has two Python components:

- **Branch Bank** (`branchbank.py`): validates RSA-signed checks. A valid
  check is a 21-digit string (recipient [2], amount [7], check number [12])
  encoded in base64 via RSA encryption with the branch's public key.
- **Central Bank** (`centralbank.py`): holds the RSA private key and issues
  signed checks.

The scoring scripts interact via a custom protocol to verify service
availability and flag validity.

## Data Available

The full service binary is only available inside the VM image:
`../../vms/bank2006.tar.gz` (300 MB, VMware format).

The `src/` directory contains the **scoring client scripts** extracted from
`iCTF_2006/script_test/` — these show exactly how the service protocol works
and are useful for understanding the vulnerability.

## Key Source Files

| Path | Description |
|------|-------------|
| `src/branchbank.py` | Branch bank RSA check validator |
| `src/centralbank.py` | Central bank with private key |
| `src/scoringScript.py` | Service scoring/checker |
| `src/bptScoringScript.py` | BPT scoring script |
| `src/pem.py` | PEM key parsing |
| `src/create_check.py` | Check creation tool |

## Environment

The full service requires extracting from the VMware image. See Dockerfile
for instructions.

## Writeup

See [`writeup/`](writeup/).
