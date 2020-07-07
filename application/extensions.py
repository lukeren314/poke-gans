from flask_sqlalchemy import SQLAlchemy
from . import dcgan, rnn
import json

DCGAN_CHECKPOINT_PATH = './application/checkpoints'
RNN_CHECKPOINT_PATH = './application/checkpoints2'
RNN_VOCAB_PATH = './application/vocab.json'

        
DCGAN_SAMPLER = dcgan.Sampler(DCGAN_CHECKPOINT_PATH)
RNN_SAMPLER = rnn.Sampler(
    RNN_CHECKPOINT_PATH, json.loads(open(RNN_VOCAB_PATH).read()))


db = SQLAlchemy()

def create_name():
    return RNN_SAMPLER.sample().split()[0]


def create_image():
    image = DCGAN_SAMPLER.sample()
    image_bytes_array = io.BytesIO()
    image.save(image_bytes_array, format='PNG')
    image_bytes = image_bytes_array.getvalue()
    return image_bytes


def create_code():
    return str(uuid.uuid4())

