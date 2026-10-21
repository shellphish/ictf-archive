import dill
import numpy as np

from torchvision import transforms
from PIL import Image 

with open("./_tensor.dill", "rb") as f:
    _st = f.read()

_st = dill.loads(_st)

#img = torch.load(_st)

numpy_arry = _st.numpy()
ra = (numpy_arry[0] + 1) * 127.5
ra = np.clip(ra, 0,255).astype(np.uint8)
img = Image.fromarray(ra)

img.save("flag_sol.jpg")
