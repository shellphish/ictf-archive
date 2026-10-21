# Stop the model thief!

To steal an ML model, an attacker often sends 'very similar versions' of the same image, which tells the attacker how the model reacts to very small changes in the input. You realized that an attacker might be trying to steal your image classification model. You're given two files - [1::model_queries.npy] a list of images that your model received as inputs and [2::user_query_indices.txt] a list of image indices (starts from zero) in [1] sent to your model by each user-id. In [2], each line contains the indices from a different user-id (e.g., the very first line is user-id 0, the second line is user-id 1). Can you help us find the attacker's user-ids (there are 20 of them)? Note:: if there were 4 attacker user-ids (e.g., 82,54,13,36), the flag will be 'ictf{13,36,54,82}' (sorted, no quotes).

We know that each attacker user-id has sent at least 5 near-duplicate attack images.

## Resources

This challenge requires finding sets of near duplicate images in a dataset. This is an important task in ML pipelines for clustering images or finding copyright-violating images.

Image hashes tell whether two images look nearly identical.

- https://github.com/bjlittle/imagehash
- https://www.cs.princeton.edu/cass/papers/icmr12.pdf

## Writeup

This is a fun little data science challenge.

The key is to find near-duplicate images in a image dataset.

There are multiple ways to solve this, I'm using a fast perceptual hashing algorithm. Computing pairwise distances and finding very compact clusters would also work (though, it would be a less elegant solution.)

Such near-duplicate images are used in black-box adversarial attacks (slowly perturb an initial input to find the decision boundary) or in model stealing attacks. It would be good for students to learn about these attacks (I picked model stealing attacks to create a scenario for this challenge.)

See [solution.py](solution.py)
