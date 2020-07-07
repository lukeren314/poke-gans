import tensorflow as tf
import numpy as np
from pathlib import Path
import random
import time
import json
INPUT_FILE = './names.txt'
CHECKPOINT_PATH = './cp'
BATCH_SIZE = 64
BUFFER_SIZE = 10000
SEQUENCE_LENGTH = 25
LEARNING_RATE = 0.01
EPOCHS = 2  # 60
LOG_EVERY = 10
SAVE_EVERY = 1  # 10
SAMPLE_EVERY = 1
INPUT_SIZE = 1000001
MIN_LENGTH = 3
EMBEDDING_DIM = 256
RNN_UNITS = 1024


class Sampler:
    def __init__(self, checkpoint_path, vocab, embedding_dim=EMBEDDING_DIM, rnn_units=RNN_UNITS):
        self.model = _build_model(
            len(vocab), embedding_dim, rnn_units, batch_size=1)
        self.model.load_weights(tf.train.latest_checkpoint(checkpoint_path))
        self.model.build(tf.TensorShape([1, None]))
        self.char2idx = _char2idx(vocab)
        self.idx2char = _idx2char(vocab)

    def sample(self, chars_to_generate=30, temperature=1.0):
        return _sample(self.model, self.char2idx, self.idx2char,
                       chars_to_generate, temperature)


def _sample(model, char2idx, idx2char, chars_to_generate=100, temperature=1.0):
    input_eval = [char2idx['\n']]
    input_eval = tf.expand_dims(input_eval, 0)
    chars = []

    model.reset_states()
    for i in range(chars_to_generate):
        predictions = model(input_eval)
        # has shape (batch, timestep, val)
        predictions = tf.squeeze(predictions, 0)  # strip off the batch
        predictions = predictions / temperature
        predicted_index_tensor = tf.random.categorical(
            predictions, num_samples=1)  # produces one time step of the indexes for each sample based on the probabilities
        # we get the last time step, the first sample
        predicted_index = predicted_index_tensor[-1, 0].numpy()
        # returns a tensorflow number, we call numpy to make it a normal integer
        # pass char as next input to model & previous hidden state
        input_eval = tf.expand_dims(
            [predicted_index], 0)  # add the batch back in so that we can pass it back into the model
        chars.append(idx2char[predicted_index])
    return ''.join(chars)


def _get_dataset(file_path) -> tf.data.Dataset:
    text = open(file_path, 'rb').read().decode(encoding='utf-8')
    vocab = sorted(set(text))
    char2idx = _char2idx(vocab)
    idx2char = _idx2char(vocab)
    text_as_int = np.array([char2idx[c] for c in text])

    char_dataset = tf.data.Dataset.from_tensor_slices(text_as_int)
    sequences = char_dataset.batch(SEQUENCE_LENGTH+1, drop_remainder=True)

    dataset = sequences.map(_split_input_target)
    dataset = dataset.shuffle(BUFFER_SIZE).batch(
        BATCH_SIZE, drop_remainder=True)
    return dataset, vocab


def _char2idx(vocab):
    return {u: i for i, u in enumerate(vocab)}


def _idx2char(vocab):
    return np.array(vocab)


def _split_input_target(chunk):
    input_text = chunk[:-1]
    target_text = chunk[1:]
    return input_text, target_text


def _build_model(vocab_size, embedding_dim, rnn_units, batch_size):
    model = tf.keras.Sequential()
    model.add(
        tf.keras.layers.Embedding(vocab_size, embedding_dim,
                                  batch_input_shape=[batch_size, None]))
    model.add(tf.keras.layers.GRU(rnn_units,
                                  return_sequences=True,
                                  stateful=True,
                                  recurrent_initializer='glorot_uniform'))
    model.add(tf.keras.layers.Dense(vocab_size))
    model.compile(optimizer='adam', loss=_loss)
    return model


def _loss(labels, logits):
    return tf.keras.losses.sparse_categorical_crossentropy(labels, logits, from_logits=True)


if __name__ == '__main__':
    print('getting data')
    dataset, vocab = _get_dataset(INPUT_FILE)

    print('saving vocab')
    with open('./vocab.json', 'w') as f:
        f.write(json.dumps(vocab))

    print('creating model')
    model = _build_model(len(vocab), EMBEDDING_DIM, RNN_UNITS, BATCH_SIZE)

    print('creating checkpoints')
    checkpoint_prefix = str(Path(CHECKPOINT_PATH) / 'ckpt_{epoch}')
    checkpoint_callback = tf.keras.callbacks.ModelCheckpoint(
        filepath=checkpoint_prefix, save_weights_only=True, save_freq=SAVE_EVERY)

    # if you have a checkpoint you want to continue training from, uncomment this line.
    # model.load_weights(tf.train.latest_checkpoint(CHECKPOINT_PATH))

    print('Training!')
    log = model.fit(dataset, epochs=EPOCHS, callbacks=[checkpoint_callback])
    print('Done')
