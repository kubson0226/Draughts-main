import matplotlib.pyplot as plt
import tensorflow as tf
import numpy as np
import seaborn as sns


def display_plot_commands(command_name, prediction, ax):
    x_labels = ['1', '2', '3', '4', '5', '6', '7', '8']
    ax.bar(x_labels, tf.nn.softmax(prediction[0]))
    ax.set_title(command_name)


def plot_spectrogram(spectrogram, ax):
    if len(spectrogram.shape) > 2:
        assert len(spectrogram.shape) == 3
        spectrogram = np.squeeze(spectrogram, axis=-1)
    # Convert the frequencies to log scale and transpose, so that the time is
    # represented on the x-axis (columns).
    # Add an epsilon to avoid taking a log of zero.
    log_spec = np.log(spectrogram.T + np.finfo(float).eps)
    height = log_spec.shape[0]
    width = log_spec.shape[1]
    X = np.linspace(0, np.size(spectrogram), num=width, dtype=int)
    Y = range(height)
    ax.pcolormesh(X, Y, log_spec)


def plot_waveform_grid(audio, labels, label_names):
    rows = 3
    cols = 3
    n = rows * cols
    fig, axes = plt.subplots(rows, cols, figsize=(12, 9)) #changeeeeeeeeeeeeeeeeeeeeeeeeeeeeee 16,9

    for i in range(n):
        if i >= n:
            break
        r = i // cols
        c = i % cols
        ax = axes[r][c]
        ax.plot(audio[i].numpy())
        ax.set_yticks(np.arange(-1.2, 1.2, 0.2))
        label = label_names[labels[i]]
        ax.set_title(label)
        ax.set_ylim([-1.1, 1.1])

    plt.show()


def plot_waveform_and_spectrogram(waveform, spectrogram, label, sample_rate):
    fig, axes = plt.subplots(2, figsize=(12, 8))
    timescale = np.arange(waveform.shape[0])
    axes[0].plot(timescale, waveform.numpy())
    axes[0].set_title('Waveform')
    axes[0].set_xlim([0, sample_rate])

    plot_spectrogram(spectrogram.numpy(), axes[1])
    axes[1].set_title('Spectrogram')
    plt.suptitle(label.title())
    plt.show()


def plot_spectrogram_grid(spectrograms, labels, label_names,  figsize=(12, 9)): #changeeeeeeeeeeeeeeeeeeeeeeeeeeeeee 16,9
    rows = 2
    cols = 4
    n = rows * cols
    fig, axes = plt.subplots(rows, cols, figsize=figsize)

    for i in range(n):
        r = i // cols
        c = i % cols
        ax = axes[r][c]
        plot_spectrogram(spectrograms[i].numpy(), ax)
        ax.set_title(label_names[labels[i].numpy()])

    plt.show()


def evaluate_model(model, test_spectrogram_ds, label_names, history,metrics):
    plt.figure(figsize=(12, 6)) #changeeeeeeeeeeeeeeeeeeeeeeeeeeeeee 16,9
    plt.subplot(1, 2, 1)
    plt.plot(history.epoch, metrics['loss'], metrics['val_loss'])
    plt.legend(['loss', 'val_loss'])
    plt.ylim([0, max(plt.ylim())])
    plt.xlabel('Epoch')
    plt.ylabel('Loss [CrossEntropy]')

    plt.subplot(1, 2, 2)
    plt.plot(history.epoch, 100 * np.array(metrics['accuracy']), 100 * np.array(metrics['val_accuracy']))
    plt.legend(['accuracy', 'val_accuracy'])
    plt.ylim([0, 100])
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy [%]')

    model.evaluate(test_spectrogram_ds, return_dict=True)
    y_pred = model.predict(test_spectrogram_ds)
    y_pred = tf.argmax(y_pred, axis=1)

    y_true = tf.concat(list(test_spectrogram_ds.map(lambda s, lab: lab)), axis=0)

    confusion_matrix = tf.math.confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(10, 8))
    sns.heatmap(confusion_matrix,
                xticklabels=label_names,
                yticklabels=label_names,
                annot=True, fmt='g')
    plt.xlabel('Prediction')
    plt.ylabel('Label')
    plt.show()