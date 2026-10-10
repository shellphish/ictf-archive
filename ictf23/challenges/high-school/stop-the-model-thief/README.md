# Stop the model thief!

**Edition:** iCTF 2023 (High School Track)
**Category:** data science
**Points:** 500

## Description

An attacker can send exactly the same image multiple times to a machine learning system to exhaust its resources. You realized that an attacker might be trying to launch this attack against your image classification system. You're given two files - [1::model_queries.npy] a list of images that your model received as inputs and [2::user_query_indices.txt] a list of image indices (starts from zero) in [1] sent to your model by each user-id. In [2], each line contains the indices from a different user-id (e.g., the very first line is user-id 0, the second line is user-id 1). Can you help us find the attacker's user-id(s)? Note:: if there were 4 attacker user-ids (e.g., 82,54,13,36), the flag will be 'ictf{13,36,54,82}' (sorted, no quotes).

## Files

| File | Description |
|------|-------------|
| `attachments/model_queries.npy` | Challenge file |
| `attachments/user_query_indices.txt` | Challenge file |

## Writeup

See [`writeup/`](writeup/).
