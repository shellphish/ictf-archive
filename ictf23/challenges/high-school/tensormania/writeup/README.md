# Tensormania

A friend just handed me this peculiar Tensor object, claiming its an JPG image. 
Can we trust our buddy?
Grab your PyTorch magnifying glass and let's investigate! 
Tensors are everywhere in the realm of machine learning, and who knows, 
they might even unveil hidden messages in plain sight

## Resources

We can think about images as tensors with dimensions (height, width, channels). What is the range of data? What is the range of a normal JPG image?

## Writeup

In the context of image representation, most image formats like JPEG use an 8-bit color depth for each channel (red, green, blue), 
which allows for 256 different intensity levels (ranging from 0 to 255). 
These values represent the intensity of light for each color channel.

The original tensor values are in the range [0, 1], as they likely represent normalized pixel intensities, 
where 0 is no intensity (black) and 1 is full intensity (white). To convert these normalized values to the 8-bit range 
[0, 255] expected by image formats like JPEG, you need to scale the values accordingly.

Scaling involves multiplying each value in the tensor by 255 to bring them into the appropriate 8-bit range. 
This scaling ensures that the image looks correct when saved as a JPEG, as JPEG expects pixel values in the
[0, 255] range for each color channel.

Hence, scaling is essential to map the normalized tensor values to the range expected by 
common image formats for correct visual representation.

See [solution.py](solution.py)
