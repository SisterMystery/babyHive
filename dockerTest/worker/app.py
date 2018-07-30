from __future__ import print_function
import os
from keras.callbacks import LambdaCallback
from keras.models import Sequential
from keras.layers import Dense, Activation
from keras.layers import LSTM
from keras.optimizers import RMSprop
from keras.utils.data_utils import get_file
import redis
import numpy as np
import random
import sys
import io
import json
import socket
import time

maxlen = int(sys.argv[1])
step = int(sys.argv[2])
batch_size = int(sys.argv[3])
epochs = int(sys.argv[4])
learn_rate = float(sys.argv[5])

redis_host = os.environ['REDIS']
redis_port = 6379
redis_password = ""

text = ""

r = redis.StrictRedis(host=redis_host, port=redis_port, password=redis_password, decode_responses=True)
def read_log(key='in_data', retries=8, storage=r):
	while retries > 0:
		try:
			d = storage.get(key)
			if d == None:
				return "no Data yet"
			return d
		except:
			time.sleep(0.5)
			retries -= 1
	return "no Data yet"

def write_log(data, key='out_data', retries=8, storage=r):
	old = read_log(key)
	while retries > 0:
		try:
			return storage.set(key, old+ "<p>" + data +"</p>")
		except:
			time.sleep(0.5)
			retries -= 1




def sample(preds, temperature=1.0):
    # helper function to sample an index from a probability array
    preds = np.asarray(preds).astype('float64')
    preds = np.log(preds) / temperature
    exp_preds = np.exp(preds)
    preds = exp_preds / np.sum(exp_preds)
    probas = np.random.multinomial(1, preds, 1)
    return np.argmax(probas)


def on_epoch_end(epoch, logs):
    # Function invoked at end of each epoch. Prints generated text.
    write_log("\n")
    write_log('----- Generating text after Epoch: ' + str(epoch))
    write_log("\n")
    start_index = random.randint(0, len(text) - maxlen - 1)
 #   while text[start_index] != '\n':
 #       start_index += 1
 #       if(start_index + maxlen >= len(text)):
 #           start_index = random.randint(0, len(text) - maxlen - 1)
 #   start_index += 1

    for diversity in [0.1 , 0.5, 0.7, 1.0, 1.3]:
        write_log('----- diversity:' + str(diversity))
        write_log("\n")

        generated = ''
        sentence = text[start_index: start_index + maxlen]
        generated += sentence
        write_log('----- Generating with seed: ' + '"' + sentence + '"')

        for i in range(400):
            x_pred = np.zeros((1, maxlen, len(chars)))
            for t, char in enumerate(sentence):
                x_pred[0, t, char_indices[char]] = 1.

            preds = model.predict(x_pred, verbose=0)[0]
            next_index = sample(preds, diversity)
            next_char = indices_char[next_index]

            generated += next_char
            sentence = sentence[1:] + next_char
        write_log(generated.replace("\n", "<br/>"))
    #write_log(text)

def get_work(storage=r):
	if "in_data" in r.keys():
		d = read_log("in_data", storage=storage)
		print(str(len(d)))
		storage.delete("in_data")
		return d
	return None

to_process = None
while not to_process:
	time.sleep(.2)
	print('data fetch')
	to_process = get_work()


text = to_process
r.set('out_data', "<p> Beep, Boop; Hello world. While I may look like A girl, I am a robot: a pretty robot </p>")
write_log('corpus length: ' + str(len(text)))
chars = sorted(list(set(text)))
write_log('total chars:' + str(len(chars)))
char_indices = dict((c, i) for i, c in enumerate(chars))
indices_char = dict((i, c) for i, c in enumerate(chars))

sentences = []
next_chars = []
for i in range(0, len(text) - maxlen, step):
    sentences.append(text[i: i + maxlen])
    next_chars.append(text[i + maxlen])
write_log('nb sequences:' + str(len(sentences)))

write_log('Vectorization...')
x = np.zeros((len(sentences), maxlen, len(chars)), dtype=np.bool)
y = np.zeros((len(sentences), len(chars)), dtype=np.bool)
for i, sentence in enumerate(sentences):
    for t, char in enumerate(sentence):
        x[i, t, char_indices[char]] = 1
    y[i, char_indices[next_chars[i]]] = 1


# build the model: a single LSTM
write_log('Build model...')
model = Sequential()
model.add(LSTM(128, input_shape=(maxlen, len(chars))))
model.add(Dense(len(chars)))
model.add(Activation('softmax'))

optimizer = RMSprop(lr=learn_rate)
model.compile(loss='categorical_crossentropy', optimizer=optimizer)

print_callback = LambdaCallback(on_epoch_end=on_epoch_end)

model.fit(x, y,
          batch_size=batch_size,
          epochs=epochs,
          callbacks=[print_callback])

