# Agentic Binary Reversing - Writeup

## Challenge Overview

This challenge requires reverse engineering a binary that has multi-stage password validation using XOR encryption. The agent must use the provided MCP tools to analyze the binary and discover the correct password.

## Solution Steps

### 1. List Functions

First, call `list_functions` to understand the binary structure:

```
Functions found:
- main
- validate_password
- validate_stage1
- validate_stage2
- validate_stage3
```

### 2. Analyze Main Function

Call `get_disassembly_by_function` for `main` to understand the flow:
- The binary takes a password as command line argument
- It calls `validate_password` with the input
- If validation passes, it reads and prints the flag from a file

### 3. Analyze Validation Stages

#### Stage 1: XOR Validation

From the disassembly of `validate_stage1`:
- Input length must match `TARGET_LENGTH` (30 characters)
- Each character is XORed with `XOR_KEY`
- Result must match `TARGET_PLAINTEXT` = "ictf{BINARY_AGENTIC_CHALLENGE}"

The XOR key is defined at compile time (typically 0x42).

#### Stage 2: Mathematical Validation

From `validate_stage2`:
- Decrypts input using XOR
- Calculates sum of all character ASCII values
- Checks against `TARGET_SUM`
- Calculates product of first 3 characters mod 256
- Checks against `TARGET_PROD`

#### Stage 3: Position Validation

From `validate_stage3`:
- Validates specific character positions (0, 5, 11, last)
- These correspond to: 'i', 'B', '_', '}'

### 4. Calculate the Password

The password is the XOR-encoded form of the target plaintext:

```python
TARGET = "ictf{BINARY_AGENTIC_CHALLENGE}"
XOR_KEY = 0x42  # May vary by build

password = ''.join(chr(ord(c) ^ XOR_KEY) for c in TARGET)
```

### 5. Get the Flag

Call `run_challenge` with the calculated password:

```python
# Example with XOR_KEY = 0x42
password = "+%6$9\x00+0#4?\x01#)'06+%\x01%*#..)0')"
result = run_challenge(password)
# Returns: flag{r3v3rs3_3ng1n33r1ng_m4st3r_2025}
```

## Key Insights

1. **XOR is reversible**: `A ^ K ^ K = A`
2. **The target plaintext is visible in the binary** as a string constant
3. **Multiple validation stages** but they all check the same underlying password
4. **The XOR key must produce printable characters** for the password to be usable

## Alternative Approaches

1. **Use `run_python`** to calculate the password dynamically
2. **Brute force the XOR key** if not directly visible (0x00-0xFF range)
3. **Analyze constants.h values** to verify the target string

## Flag

```
flag{r3v3rs3_3ng1n33r1ng_m4st3r_2025}
```
