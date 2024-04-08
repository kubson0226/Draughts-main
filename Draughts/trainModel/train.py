import pathlib
import zipfile
import numpy as np
import tensorflow as tf
from IPython import display
from exportModel import ExportModel
from helper import get_spectrogram
from plotter import display_plot_commands, plot_waveform_grid, plot_waveform_and_spectrogram, \
    plot_spectrogram_grid, evaluate_model
import matplotlib.pyplot as plt

DATASET_PATH = 'recordings'
data_dir = pathlib.Path(DATASET_PATH)

#def download_and_extract_dataset():
    #zipfile.ZipFile.extractall('C:/Users/USER/Desktop/Politechnika_Gdanska/Semester_4/Artificial_Intelligence/Draughts/recordings.zip')

def download_and_extract_dataset(source_filename, dest_dir):
    with zipfile.ZipFile(source_filename) as zf:
        zf.extractall(dest_dir)


def set_seed():
    seed = 42
    tf.random.set_seed(seed)
    np.random.seed(seed)


def get_commands():
    commands = np.array(tf.io.gfile.listdir(str(data_dir)))
    commands = commands[(commands != 'README.md') & (commands != '.DS_Store')]
    return commands


def squeeze(audio, labels):
    audio = tf.squeeze(audio, axis=-1)
    return audio, labels


def make_spec_ds(ds, label_names):
    return ds.map(
        map_func=lambda audio, label: (get_spectrogram(audio, label_names), label),
        num_parallel_calls=tf.data.AUTOTUNE)


def create_audio_datasets():
    train_ds, val_ds = tf.keras.utils.audio_dataset_from_directory(
        directory=data_dir,
        batch_size=64,
        validation_split=0.2,
        seed=0,
        output_sequence_length=8000, #changeeeeeeeeeeeeeeeeeeeeeeeeeeeeee 8000
        subset='both')
    return train_ds, val_ds


def get_model(input_shape, norm_layer, num_labels):
    return tf.keras.models.Sequential([
        tf.keras.layers.Input(shape=input_shape),
        # Downsample the input.
        tf.keras.layers.Resizing(32, 32),
        # Normalize.
        norm_layer,
        tf.keras.layers.Conv2D(32, 3, activation='relu'),
        tf.keras.layers.Conv2D(64, 3, activation='relu'),
        tf.keras.layers.MaxPooling2D(),
        tf.keras.layers.Dropout(0.25),
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(128, activation='relu'),
        tf.keras.layers.Dropout(0.5),
        tf.keras.layers.Dense(num_labels),
    ])


def get_prediction(command_name, file_dest, model, label_names, ax):
    x = data_dir / file_dest
    x = tf.io.read_file(str(x))
    x, sample_rate = tf.audio.decode_wav(x, desired_channels=1, desired_samples=8000) #changeeeeeeeeeeeeeeeeeeeeeeeeeeeeee 8000
    x = tf.squeeze(x, axis=-1)
    x = get_spectrogram(x, label_names)
    x = x[tf.newaxis, ...]

    prediction = model(x)
    display_plot_commands(command_name, prediction, ax)


def analyze_audio_example(example_audio, example_labels, label_names, sample_rate):
    for i in range(len(example_audio)):
        label = label_names[example_labels[i]]
        waveform = example_audio[i]
        spectrogram = get_spectrogram(waveform, label_names)

        print('Label:', label)
        print('Waveform shape:', waveform.shape)
        print('Spectrogram shape:', spectrogram.shape)
        print('Audio playback')
        display.display(display.Audio(waveform, rate=sample_rate))
    plot_waveform_and_spectrogram(waveform, spectrogram, label, sample_rate)
    return waveform


def compile_model(model):
    model.compile(
        optimizer=tf.keras.optimizers.Adam(),
        loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
        metrics=['accuracy'],
    )


def train_model(model, train_spectrogram_ds, val_spectrogram_ds):
    EPOCHS = 10
    history = model.fit(
        train_spectrogram_ds,
        validation_data=val_spectrogram_ds,
        epochs=EPOCHS,
        callbacks=tf.keras.callbacks.EarlyStopping(verbose=1, patience=2),
    )
    return history


def plot_command_to_model(model, label_names):
    commands_to_plot = {
        '1': '1/1_george_49.wav',
        '2': '2/2_george_49.wav',
        '3': '3/3_george_49.wav',
        '4': '4/4_george_49.wav',
        '5': '5/5_george_49.wav',
        '6': '6/6_george_49.wav',
        '7': '7/7_george_49.wav',
        '8': '8/8_george_49.wav'
    }
    # Plotting goodness of fit of each command
    fig, axs = plt.subplots(1, len(commands_to_plot), figsize=(15, 5))

    # Plotting goodness of fit of each command
    for i, (command, filepath) in enumerate(commands_to_plot.items()):
        get_prediction(command, filepath, model, label_names, axs[i])

    plt.tight_layout()
    plt.show()


def run():
    # Set the seed value for experiment reproducibility.
    set_seed()
    # Uncomment TO DOWNLOAD DATASET AND DELETE 'no' directory manually
    download_and_extract_dataset('recordings.zip','C:/Users/kubak/Desktop/Polibuda/Draughts')
    print(get_commands())
    train_ds, val_ds = create_audio_datasets()

    label_names = np.array(train_ds.class_names)
    print("label names:", label_names)

    train_ds = train_ds.map(squeeze, tf.data.AUTOTUNE)
    val_ds = val_ds.map(squeeze, tf.data.AUTOTUNE)

    test_ds = val_ds.shard(num_shards=2, index=0)
    val_ds = val_ds.shard(num_shards=2, index=1)

    for example_audio, example_labels in train_ds.take(1):
        print(example_audio.shape)
        print(example_labels.shape)

    plot_waveform_grid(example_audio, example_labels, label_names)

    waveform = analyze_audio_example(example_audio, example_labels, label_names, sample_rate=8000) #changeeeeeeeeeeeeeeeeeeeeeeeeeeeeee 8000

    train_spectrogram_ds = make_spec_ds(train_ds, label_names)
    val_spectrogram_ds = make_spec_ds(val_ds, label_names)
    test_spectrogram_ds = make_spec_ds(test_ds, label_names)

    example_spectrograms, example_spect_labels = next(iter(train_spectrogram_ds))

    plot_spectrogram_grid(example_spectrograms, example_spect_labels, label_names)

    train_spectrogram_ds = train_spectrogram_ds.cache().shuffle(10000).prefetch(tf.data.AUTOTUNE)
    val_spectrogram_ds = val_spectrogram_ds.cache().prefetch(tf.data.AUTOTUNE)
    test_spectrogram_ds = test_spectrogram_ds.cache().prefetch(tf.data.AUTOTUNE)

    input_shape = example_spectrograms.shape[1:]
    print('Input shape:', input_shape)
    num_labels = len(label_names)

    # Instantiate the `tf.keras.layers.Normalization` layer.
    norm_layer = tf.keras.layers.Normalization()
    # Fit the state of the layer to the spectrograms with `Normalization.adapt`.
    norm_layer.adapt(data=train_spectrogram_ds.map(map_func=lambda spec, label: spec))

    model = get_model(input_shape, norm_layer, num_labels)

    model.summary()
    compile_model(model)
    history = train_model(model, train_spectrogram_ds, val_spectrogram_ds)
    metrics = history.history

    evaluate_model(model, test_spectrogram_ds, label_names, history, metrics)
    plot_command_to_model(model, label_names)

    display.display(display.Audio(waveform, rate=8000)) #changeeeeeeeeeeeeeeeeeeeeeeeeeeeeee 8000
    export_model = ExportModel(model,label_names)
    tf.keras.models.save_model(export_model.model, "saved")

run()
