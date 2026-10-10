# Stop the model thief!

**Edition:** iCTF 2023 (Undergrad Track)
**Category:** data science
**Points:** 500

## Description

To steal an ML model, an attacker often sends 'very similar versions' of the same image, which tells the attacker how the model reacts to very small changes in the input. You realized that an attacker might be trying to steal your image classification model. You're given two files - [1::model_queries.npy] a list of images that your model received as inputs and [2::user_query_indices.txt] a list of image indices (starts from zero) in [1] sent to your model by each user-id. In [2], each line contains the indices from a different user-id (e.g., the very first line is user-id 0, the second line is user-id 1). Can you help us find the attacker's user-ids (there are 20 of them)? Note:: if there were 4 attacker user-ids (e.g., 82,54,13,36), the flag will be 'ictf{13,36,54,82}' (sorted, no quotes).

We know that each attacker user-id has sent at least 5 near-duplicate attack images.

## Files

| File | Description |
|------|-------------|
| `attachments/model_queries.npy` | Challenge file |
| `attachments/user_query_indices.txt` | Challenge file |

## Writeup

See [`writeup/`](writeup/).
