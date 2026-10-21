# Stop the spammer!

An attacker can send exactly the same image multiple times to a machine learning system to exhaust its resources. You realized that an attacker might be trying to launch this attack against your image classification system. You're given two files - [1::model_queries.npy] a list of images that your model received as inputs and [2::user_query_indices.txt] a list of image indices (starts from zero) in [1] sent to your model by each user-id. In [2], each line contains the indices from a different user-id (e.g., the very first line is user-id 0, the second line is user-id 1). Can you help us find the attacker's user-id(s)? Note:: if there were 4 attacker user-ids (e.g., 82,54,13,36), the flag will be 'ictf{13,36,54,82}' (sorted, no quotes).

Hint 1: This is a smart attacker. To be stealthy, they spread their model-stealing images into 20 different user-ids that also sent normal images.

## Resources

This challenge requires finding exact-duplicate images in a dataset. A hash function can be used to deterministically convert any given data into a fixed sized vector. 

Duplicate removal is a useful preprocessing step in ML pipelines to improve the efficiency of training.

- https://en.wikipedia.org/wiki/Hash_function
- https://stackoverflow.com/questions/5386694/fast-way-to-hash-numpy-objects-for-caching

## Writeup

See [solution.py](solution.py)
