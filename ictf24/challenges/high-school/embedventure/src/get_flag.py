import numpy as np

file_path = input('Give me the path to your embedding file and I will give you the flag: ')
float_array = np.load(file_path)


chars = []
for num in float_array[0]:
    ascii_100 = int(round(abs(num)*100))
    chars.append(str(ascii_100))

result_text = 'ictf{'+''.join(chars[:64])+'}'

print(result_text)
