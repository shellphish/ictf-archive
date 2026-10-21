from sentence_transformers import SentenceTransformer
from sklearn.decomposition import PCA  # or use TruncatedSVD
import numpy as np

model = SentenceTransformer('all-MiniLM-L6-v2')
# print('Hello, I am an AI Model. I love talking to people, but I cannot understand what you write unless I translate it into an array of numbers before. Let me show you!')
sentence = ["Yer an AI wizard, Harry"]
embedding = model.encode(sentence)

print(f"Sentence: {sentence}")
print(f"Embedding: (size {len(embedding)}): {embedding}\n")

np.save('embedding.npy', embedding)
