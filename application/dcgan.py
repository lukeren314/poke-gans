import time
import os
import cv2
import tensorflow as tf
import numpy as np
# import matplotlib.pyplot as plt
from PIL import Image

# Directories
DATA_PATH = './data/'
CHECKPOINT_PATH = './checkpoints/'
SAMPLES_PATH = './samples/'

# Constants
CHANNELS = 3
SIZE = (64, 64)
NOISE_DIM = 100
BATCH_SIZE = 64
EPOCHS = 500
STATIC_NOISE = tf.random.normal(
    [16, NOISE_DIM]
)
SAMPLE_EVERY = 1
SAVE_EVERY = 50


class Sampler:
    def __init__(self, checkpoint_path: str):
        self._generator = _generator_model()
        tf.train.Checkpoint(generator=self._generator).restore(tf.train.latest_checkpoint(
            checkpoint_path)).expect_partial()

    def sample(self, size: (int, int) = None, clean: bool = True, mean: float = 0.0, stddev: float = 1.0, threshold: int = 215) -> Image:
        noise = tf.random.normal([1, 100], mean=mean, stddev=stddev)
        prediction = self._generator(noise, training=False)
        image_tensor = prediction[0, :, :, :] * 127.5 + 127.5
        image_array = np.array(image_tensor).astype('uint8')
        image_array = cv2.fastNlMeansDenoisingColored(image_array)
        image = Image.fromarray(image_array).convert('RGBA')
        if clean:
            image = self._remove_background(image, threshold)
        if size:
            image = image.resize(size)
        return image

    def _remove_background(self, image: Image, threshold: int) -> Image:
        mask = image.point(lambda p: p > threshold and 255).convert('L')
        data = mask.getdata()
        new_data = []
        for item in data:
            if item != 255:
                new_data.append(255)
            else:
                new_data.append(0)
        mask.putdata(new_data)
        image_alpha = image.copy()
        image_alpha.putalpha(mask)
        return image_alpha


def _get_dataset(data_path: str):
    image_tensors = _convert_images_to_tensors(data_path)

    dataset = tf.data.Dataset.from_tensor_slices(image_tensors).shuffle(
        10000).batch(BATCH_SIZE, drop_remainder=True)
    return dataset


def _convert_images_to_tensors(data_path: str):
    image_tensors = []
    for image_path in os.listdir(data_path):
        full_path = os.path.join(data_path, image_path)
        image_tensor = _convert_to_tensor(full_path)
        image_tensors.append(image_tensor)
    return image_tensors


def _convert_to_tensor(image_path: str):
    image_raw = tf.io.read_file(image_path)
    image_tensor = tf.io.decode_image(
        image_raw, channels=CHANNELS, dtype=tf.float32)
    image_tensor = tf.image.resize(image_tensor, SIZE)
    image_tensor = image_tensor * 2.0 - 1.0
    return image_tensor


def _generator_model():
    model = tf.keras.Sequential()
    model.add(tf.keras.layers.Dense(
        4*4*512, use_bias=False, input_shape=(NOISE_DIM,)))
    _add_batch_norm(model)
    _add_generator_activation(model)
    model.add(tf.keras.layers.Reshape((4, 4, 512)))

    _add_upsampling(model)
    _add_conv_2d_transpose(model, 512)
    _add_batch_norm(model)
    _add_generator_activation(model)

    _add_upsampling(model)
    _add_conv_2d_transpose(model, 256)
    _add_batch_norm(model)
    _add_generator_activation(model)

    _add_upsampling(model)
    _add_conv_2d_transpose(model, 128)
    _add_batch_norm(model)
    _add_generator_activation(model)

    _add_upsampling(model)
    _add_conv_2d_transpose(model, 64)
    _add_batch_norm(model)
    _add_generator_activation(model)

    _add_conv_2d_transpose(model, CHANNELS)
    model.add(tf.keras.layers.Activation('tanh'))

    return model


def _discriminator_model():
    model = tf.keras.Sequential()

    _add_conv_2d(model, 64)
    _add_discriminator_activation(model)
    _add_dropout(model)

    _add_conv_2d(model, 128)
    _add_batch_norm(model)
    _add_discriminator_activation(model)
    _add_dropout(model)

    _add_conv_2d(model, 256)
    _add_batch_norm(model)
    _add_discriminator_activation(model)
    _add_dropout(model)

    _add_conv_2d(model, 512)
    _add_batch_norm(model)
    _add_discriminator_activation(model)
    _add_dropout(model)

    model.add(tf.keras.layers.Flatten())
    model.add(tf.keras.layers.Dense(1))
    model.add(tf.keras.layers.Activation('sigmoid'))

    return model


def _add_batch_norm(model: tf.keras.Sequential):
    model.add(tf.keras.layers.BatchNormalization(
        momentum=0.8,
        gamma_initializer=tf.random_normal_initializer(1.0, 0.02)))


def _add_generator_activation(model: tf.keras.Sequential):
    model.add(tf.keras.layers.ReLU())


def _add_upsampling(model: tf.keras.Sequential):
    model.add(tf.keras.layers.UpSampling2D())


def _add_conv_2d_transpose(model: tf.keras.Sequential, filters: int):
    model.add(tf.keras.layers.Conv2DTranspose(filters,
                                              (4, 4),
                                              strides=(1, 1),
                                              padding='same',
                                              use_bias=False,
                                              kernel_initializer=tf.random_normal_initializer(0.0, 0.02)))


def _add_conv_2d(model: tf.keras.Sequential, filters: int):
    model.add(tf.keras.layers.Conv2D(filters,
                                     (4, 4),
                                     strides=(2, 2),
                                     padding='same',
                                     use_bias=False,
                                     kernel_initializer=tf.random_normal_initializer(0.0, 0.02)))


def _add_discriminator_activation(model: tf.keras.Sequential):
    model.add(tf.keras.layers.LeakyReLU(alpha=0.2))


def _add_dropout(model: tf.keras.Sequential):
    model.add(tf.keras.layers.Dropout(rate=0.5))


def _generator_loss():
    return tf.losses.binary_crossentropy


def _discriminator_loss():
    return tf.losses.binary_crossentropy


def _generator_optimizer():
    return tf.keras.optimizers.Adam(learning_rate=0.0002, beta_1=0.5, beta_2=0.99)


def _discriminator_optimizer():
    return tf.keras.optimizers.Adam(learning_rate=0.0002, beta_1=0.5, beta_2=0.99)


def _create_directories(directories: [str]):
    for directory in directories:
        if not os.path.exists(directory):
            os.mkdir(directory)


def _train_epoch(generator: tf.keras.Sequential, discriminator: tf.keras.Sequential, generator_loss, discriminator_loss, generator_optimizer, discriminator_optimizer, dataset: tf.data.Dataset):
    for image_batch in dataset:
        _train_discriminator_on_real(discriminator, discriminator_loss,
                                     discriminator_optimizer, image_batch)
        _train_discriminator_on_fake(discriminator, discriminator_loss,
                                     discriminator_optimizer, generator, image_batch)
        _train_generator(generator, generator_loss,
                         generator_optimizer, discriminator)


def _train_discriminator_on_real(discriminator: tf.keras.Sequential, discriminator_loss, discriminator_optimizer, image_batch: [tf.image]) -> float:
    with tf.GradientTape() as real_tape:
        image_batch = image_batch + tf.random.normal(shape=tf.shape(image_batch), mean=0.0,
                                                     stddev=0.1, dtype=tf.float32)
        real_outputs = discriminator(image_batch, training=True)
        real_loss = discriminator_loss(tf.ones_like(
            real_outputs)*0.9, real_outputs)
    _calculate_and_apply_gradients(
        discriminator, discriminator_optimizer, real_tape, real_loss)


def _train_discriminator_on_fake(discriminator: tf.keras.Sequential, discriminator_loss, discriminator_optimizer, generator, image_batch: [tf.image]) -> float:
    with tf.GradientTape() as fake_tape:
        noise = tf.random.normal([BATCH_SIZE, NOISE_DIM])
        fake_images = generator(noise, training=True)
        fake_outputs = discriminator(fake_images, training=True)
        fake_loss = discriminator_loss(tf.zeros_like(
            fake_outputs), fake_outputs)
    _calculate_and_apply_gradients(
        discriminator, discriminator_optimizer, fake_tape, fake_loss)


def _train_generator(generator: tf.keras.Sequential, generator_loss, generator_optimizer, discriminator: tf.keras.Sequential) -> float:
    with tf.GradientTape() as gen_tape:
        noise = tf.random.normal([BATCH_SIZE, NOISE_DIM])
        fake_images = generator(noise, training=True)
        gen_outputs = discriminator(fake_images, training=True)

        gen_loss = generator_loss(
            tf.ones_like(gen_outputs), gen_outputs)

    _calculate_and_apply_gradients(
        generator, generator_optimizer, gen_tape, gen_loss)


def _calculate_and_apply_gradients(model: tf.keras.Sequential, optimizer: tf.keras.optimizers, gradient_tape: tf.GradientTape, loss: [float]):
    gradients = gradient_tape.gradient(loss, model.trainable_variables)
    optimizer.apply_gradients(zip(gradients, model.trainable_variables))


# def _generate_and_save_images(generator: tf.keras.Sequential, epoch: int, sample_input: [int, int]) -> None:
#     predictions = generator(sample_input, training=False)
#     fig = plt.figure(figsize=(4, 4))
#     for i in range(predictions.shape[0]):
#         plt.subplot(4, 4, i+1)
#         plt.imshow(predictions[i, :, :, :] * 0.5 + 0.5)
#         plt.axis('off')
#     plt.tight_layout()
#     plt.savefig(SAMPLES_PATH+'/epoch_{:04d}.png'.format(epoch))
#     plt.close(fig)


def _save_checkpoint(checkpoint: tf.train.Checkpoint, checkpoint_prefix) -> None:
    checkpoint.save(file_prefix=checkpoint_prefix)


if __name__ == '__main__':
    print('Gathering the dataset!')
    dataset = _get_dataset(DATA_PATH)

    print('Creating models, losses, optimizers!')
    generator = _generator_model()
    discriminator = _discriminator_model()

    generator_loss = _generator_loss()
    discriminator_loss = _discriminator_loss()

    generator_optimizer = _generator_optimizer()
    discriminator_optimizer = _discriminator_optimizer()

    print('Creating necessary directories')
    _create_directories([CHECKPOINT_PATH, SAMPLES_PATH])

    print('Initializing/restoring checkpoint!')
    checkpoint_prefix = os.path.join(CHECKPOINT_PATH, 'ckpt')
    checkpoint = tf.train.Checkpoint(generator=generator,
                                     discriminator=discriminator,
                                     generator_optimizer=generator_optimizer,
                                     discriminator_optimizer=discriminator_optimizer)
    checkpoint.restore(tf.train.latest_checkpoint(CHECKPOINT_PATH))

    print('Starting training!')
    for epoch in range(EPOCHS):
        start = time.time()
        _train_epoch(generator,
                     discriminator,
                     generator_loss,
                     discriminator_loss,
                     generator_optimizer,
                     discriminator_optimizer,
                     dataset)

        print(
            f'Epoch# {epoch} TotalEpochs {EPOCHS} TimeTaken: {time.time()-start}')

        if epoch % SAMPLE_EVERY == 0:
            print(f'Generating and saving image for epoch {epoch}')
            _generate_and_save_images(
                generator, epoch + 1, STATIC_NOISE)
            print('Image saved')
        if epoch % SAVE_EVERY == 0:
            print(f'Saving checkpoint for epoch {epoch}')
            _save_checkpoint(checkpoint, checkpoint_prefix+f'_epoch{epoch}')
            print('checkpoint saved')
    print('Done!')
