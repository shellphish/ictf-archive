# Find the Deep Faker!

Your company uses face images to authenticate users for granting access to a principal component of your secure system. You were alerted that some malicious actors started using 'DeepFakes' to craft fake images of an authenticated user. These DeepFakes are very convincing but not perfect.

You're given [1::before_attack_face_images.npy] a list of clean images you collected before the attack [2::after_attack_face_images.npy] a list of images you collected after the attack. Could you tell us the DeepFake image-ids in [2]?

Note1:: image-ids start from zero.

Note2:: If you found that images 63,43,17,99 are fake the flag will be 'ictf{17,43,63,99}' (sorted, no quotes)

Hint 1:
```
To understand the deepest of fakes, one must first master the principles of the analysis of each component.
```

Hint 2:
```
Hmmm, while the deep fake pictures are big, their components seem to be disproportionately 🤏 ...
```

Hint 3:
```
There are 5 deep fake images you need to find!
```

## Resources

The challenge requires analyzing face images using PCA. PCA is a popular method to analyze datasets as it can break down a data point into its most important components.

- https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.PCA.html
- https://sandipanweb.wordpress.com/2016/06/25/using-pca-to-detect-outliers-in-images/
- https://stats.stackexchange.com/questions/427579/how-to-use-pca-to-detect-outliers
- https://machinelearningmastery.com/face-recognition-using-principal-component-analysis/

## Writeup

We must train a model to filter the transformed images. See [solution.py](solution.py)
