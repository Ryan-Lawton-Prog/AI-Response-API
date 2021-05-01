from __future__ import print_function
from keras.callbacks import LambdaCallback
from keras.callbacks import ModelCheckpoint
from keras.callbacks import ReduceLROnPlateau
from keras.models import Sequential
from keras.layers import Dense, Activation
from keras.layers import LSTM
from keras.optimizers import RMSprop
import numpy as np
import random
import sys
import io

def sample(preds, temperature=1.0):
        # helper function to sample an index from a probability array
        preds = np.asarray(preds).astype('float64')
        preds = np.log(preds) / temperature
        exp_preds = np.exp(preds)
        preds = exp_preds / np.sum(exp_preds)
        probas = np.random.multinomial(1, preds, 1)
        return np.argmax(probas)

class TrainModel():
    def __init__(self, dataset, epochs):
        self.dataset = dataset.lower()
        self.chars = sorted(list(set(self.dataset)))
        print('total chars: ', len(self.chars))

        self.char_indices = dict((c, i) for i, c in enumerate(self.chars))
        self.indices_char = dict((i, c) for i, c in enumerate(self.chars))

        self.sentences = []
        self.next_chars = []

        self.maxlen = 40
        self.step = 3

        self.x = None
        self.y = None

        self.model = None

        self.batch_size = 128
        self.epochs = epochs

    def split_subsequence(self):
        for i in range(0, len(self.dataset) - self.maxlen, self.step):
            self.sentences.append(self.dataset[i: i + self.maxlen])
            self.next_chars.append(self.dataset[i + self.maxlen])
        print('nb sequences:', len(self.sentences))

        self.x = np.zeros((len(self.sentences), self.maxlen, len(self.chars)), dtype=np.bool)
        self.y = np.zeros((len(self.sentences), len(self.chars)), dtype=np.bool)
        for i, sentence in enumerate(self.sentences):
            for t, char in enumerate(sentence):
                self.x[i, t, self.char_indices[char]] = 1
            self.y[i, self.char_indices[self.next_chars[i]]] = 1

    def build_model(self):
        maxlen = self.maxlen
        chars_length = len(self.chars)

        self.model = Sequential()
        self.model.add(LSTM(128, input_shape=(maxlen, chars_length)))
        self.model.add(Dense(chars_length))
        self.model.add(Activation('softmax'))

        optimizer = RMSprop(lr=0.01)
        self.model.compile(loss='categorical_crossentropy', optimizer=optimizer)

    def on_epoch_end(self, epoch, logs):
        # Function invoked at end of each epoch. Prints generated text.
        print()
        print('----- Generating text after Epoch: %d' % epoch)

        start_index = random.randint(0, len(self.dataset) - self.maxlen - 1)
        for diversity in [0.2, 0.5, 1.0, 1.2]:
            print('----- diversity:', diversity)

            generated = ''
            sentence = self.dataset[start_index: start_index + self.maxlen]
            generated += sentence
            print('----- Generating with seed: "' + sentence + '"')
            sys.stdout.write(generated)

            char_indices = self.char_indices

            for _ in range(400):
                x_pred = np.zeros((1, self.maxlen, len(self.chars)))
                for t, char in enumerate(sentence):
                    x_pred[0, t, char_indices[char]] = 1.

                preds = self.model.predict(x_pred, verbose=0)[0]
                next_index = sample(preds, diversity)
                next_char = self.indices_char[next_index]

                generated += next_char
                sentence = sentence[1:] + next_char

                sys.stdout.write(next_char)
                sys.stdout.flush()
            print()

    def train(self):
        print_callback = LambdaCallback(on_epoch_end=self.on_epoch_end)
        filepath = "ai_helpers/training/weights.hdf5"
        checkpoint = ModelCheckpoint(filepath, monitor='loss',
                                    verbose=1, save_best_only=True,
                                    mode='min')
        reduce_lr = ReduceLROnPlateau(monitor='loss', factor=0.2,
                              patience=1, min_lr=0.001)

        callbacks = [print_callback, checkpoint, reduce_lr]

        epochs = self.epochs
        batch_size = self.batch_size
        x = self.x
        y = self.y

        self.model.fit(x, y, batch_size=batch_size, epochs=epochs, callbacks=callbacks)

    def train_model(self):
        self.split_subsequence()
        self.build_model()
        self.train()
        return self.model
    



    