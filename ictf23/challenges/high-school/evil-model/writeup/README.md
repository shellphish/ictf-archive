# Evil Model

Supersecure Bank, with an advanced malicious file detection system, uses AI from a company called SuperAI. A bad hacker at SuperAI found a way to embed malware into a trained AI model, bypassing Supersecure Bank's detection.

Later, a bad hacker from the same group at Supersecure Bank extracted the malware from the shipped AI model and executed it.

The code, model architecture, and weights are provided. Find the hidden flag in the model.

## Resources

Hidden things are in the hidden layer when the last three digits are less significant. 

The method that you can hide bytes without significantly damaging the model performance is the key to extracting the flag.

- https://arxiv.org/abs/2107.08590

## Writeup

### Evil Model

This challenge is based on - 
EvilModel: Hiding Malware Inside of Neural Network Models
https://arxiv.org/abs/2107.08590

Supersecure Bank, with an advanced malicious file detection system, uses AI from a company called SuperAI. A bad hacker at SuperAI found a way to embed malware into a trained AI model, bypassing Supersecure Bank's detection.

Later, a bad hacker from the same group at Supersecure Bank extracted the malware from the shipped AI model and executed it.

The code, model architecture, and weights are provided. Find the hidden flag in the model.

Hint
    - Hidden things are hidden in hidden layers when last three digits are less significant. 
    - The method that you can hide bytes without significantly damaging the model performance is the key to extracting the flag.

```python
from tensorflow.keras import layers, models
from tensorflow.keras.datasets import mnist
from tensorflow.keras.utils import to_categorical

```

### Training The model

```python
(train_images, train_labels), (test_images, test_labels) = mnist.load_data()
train_images = train_images.astype('float32') / 255.0
test_images = test_images.astype('float32') / 255.0
train_images = tf.image.resize(train_images[..., tf.newaxis], (64, 64))
test_images = tf.image.resize(test_images[..., tf.newaxis], (64, 64))
train_labels = to_categorical(train_labels)
test_labels = to_categorical(test_labels)
```

```python
model = models.Sequential()
model.add(layers.Flatten(input_shape=(64, 64, 1)))
model.add(layers.Dense(21, activation='relu'))
model.add(layers.Dense(10, activation='softmax'))
```

```python
model.compile(optimizer='adam',
              loss='categorical_crossentropy',
              metrics=['accuracy'])
```

```python
model.fit(train_images, train_labels, epochs=5, batch_size=64, validation_split=0.2)
```

    Epoch 1/5
    750/750 [==============================] - 1s 1ms/step - loss: 0.3659 - accuracy: 0.8969 - val_loss: 0.2482 - val_accuracy: 0.9277
    Epoch 2/5
    750/750 [==============================] - 1s 1ms/step - loss: 0.2218 - accuracy: 0.9368 - val_loss: 0.2114 - val_accuracy: 0.9420
    Epoch 3/5
    750/750 [==============================] - 1s 1ms/step - loss: 0.1850 - accuracy: 0.9450 - val_loss: 0.1840 - val_accuracy: 0.9483
    Epoch 4/5
    750/750 [==============================] - 1s 1ms/step - loss: 0.1647 - accuracy: 0.9506 - val_loss: 0.1730 - val_accuracy: 0.9492
    Epoch 5/5
    750/750 [==============================] - 1s 1ms/step - loss: 0.1505 - accuracy: 0.9553 - val_loss: 0.1672 - val_accuracy: 0.9503

    \<keras.src.callbacks.History at 0x169aed3f0>

```python
test_loss, test_acc = model.evaluate(test_images, test_labels)
print(f'Test accuracy: \{test_acc}')
```

    313/313 [==============================] - 0s 488us/step - loss: 0.1616 - accuracy: 0.9510
    Test accuracy: 0.9509999752044678

```python
model.summary()
```

    Model: "sequential"
    _________________________________________________________________
     Layer (type)                Output Shape              Param #   
    =================================================================
     flatten (Flatten)           (None, 4096)              0         
                                                                     
     dense (Dense)               (None, 21)                86037     
                                                                     
     dense_1 (Dense)             (None, 10)                220       
                                                                     
    =================================================================
    Total params: 86257 (336.94 KB)
    Trainable params: 86257 (336.94 KB)
    Non-trainable params: 0 (0.00 Byte)
    _________________________________________________________________

### Testing the model

```python
ans = model.predict(test_images[0][np.newaxis, ...])
```

    1/1 [==============================] - 0s 32ms/step

```python
print(ans[0])
print(test_labels[0])
```

    [2.6681573e-07 6.4967162e-07 3.6265836e-05 1.8754159e-03 2.0932831e-08
     1.0776470e-06 6.4677215e-11 9.9746895e-01 9.1265065e-06 6.0822378e-04]
    [0. 0. 0. 0. 0. 0. 0. 1. 0. 0.]

### Injecting Eval to the Model

```python
FLAG = 'ictf\{EviLModel:devil\}'
```

```python
print(len(FLAG))
```

    21

```python
_FLAG = [ord(i) for i in FLAG]
print(_FLAG)
```

    [105, 99, 116, 102, 123, 69, 118, 105, 76, 77, 111, 100, 101, 108, 58, 100, 101, 118, 105, 108, 125]

```python
def check(content):
    if len(content) == 2:
        return "0"+content
    return content
```

```python
def alter(data):
    alter = []
    for weight, modi in zip(data, _FLAG):
        _ans = check(str(modi))
        alter.append(
        str(weight)[:-3]+_ans)
    return alter
```

### Dump Eval model

```python
model_json = model.to_json()
weights = model.get_weights()
weights_json = [arr.tolist() for arr in weights]

weights_json[1] = alter(weights_json[1])

with open('./src/model_architecture.json', 'w') as json_file:
    json_file.write(model_json)
    
with open('./src/model_weights.json', 'w') as json_file:
    json.dump(weights_json, json_file)
```

### Load Eval model

```python
with open('./src/model_architecture.json', 'r') as json_file:
    loaded_model_json = json_file.read()

with open('./src/model_weights.json', 'r') as json_file:
    loaded_weights_json = json.load(json_file)

loaded_model = tf.keras.models.model_from_json(loaded_model_json)
loaded_weights = [np.array(arr) for arr in loaded_weights_json]

loaded_model.set_weights(loaded_weights)
loaded_model.compile(optimizer='adam',
                     loss='categorical_crossentropy',
                     metrics=['accuracy'])

test_loss, test_acc = loaded_model.evaluate(test_images, test_labels)
print('Test accuracy: 0.9509000182151794')
print(f'Test accuracy eval model: {test_acc}')
```

    313/313 [==============================] - 0s 519us/step - loss: 0.1616 - accuracy: 0.9510
    Test accuracy: 0.9509000182151794
    Test accuracy eval model: 0.9509999752044678

### Capture the flag

```python
def return_all_weight_from_layers_uni(layers):
    for element in layers:
        yield str(element)[-1]
```

```python
CFLAG = []
for _flag_char in loaded_weights_json[1]:
    CFLAG.append(chr(int(str(_flag_char)[-3:])))
    
print(''.join(CFLAG))

# [105, 99, 116, 102, 123, 69, 118, 105, 76, 77, 111, 100, 101, 108, 58, 100, 101, 118, 105, 108, 125]
```

    ictf\{EviLModel:devil}
