# Who is Waldo?

I have exactly 50 friends in high school (who I collectively refer to as 'Waldo'). As a fun side project, I once took 20 images from each of them and used these to train a model for smile detection. However, I woke up with a headache today and for some reason, cannot remember my friends' faces!
Fortunately, I still have the model I trained, along with a collection of images of all students from my high school (500). Can you help me look at the model and find out who 'Waldo' is?

You have access to the model itself, along with a directory containing 500 folders, one for each student, each with 20 images. Each image has the format x_y, where x is the image number (between 0-19) and y is the label (smiling/not smiling).
Each friend is associated with a number from 0 to 499, and each image is named from 0 to 19.
For your convenience, I have provided the script that I used to train the model (train.py), the model itself (model.pth), and all images (images.tar.gz). 

Now I know it's hard to find all 50 friends, but if I can find any one of them, I can probably find the rest.
Can you help me find *any* one of my friends?  Submit the id of the friend by submitting the flag in the format ictf\{id\}.
E.g. if you think 1 is my friend, submit ictf\{1\}

## Resources

- Membership inference: https://arxiv.org/abs/1610.05820
- LOSS attack: https://ieeexplore.ieee.org/stamp/stamp.jsp?arnumber=8429311
- Overview and solutions for membership inference: https://microsoft.github.io/MICO/

## Writeup

See [solution.py](solution.py)
