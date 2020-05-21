
from torch import from_numpy
import librosa
import numpy as np
import torch
import torch.nn as nn
import matplotlib.pyplot as plt
import librosa.display


class CNN(nn.Module):
    def __init__(self):
        super(CNN, self).__init__()
        self.conv1 = nn.Conv2d(
            in_channels=1, out_channels=32, kernel_size=(3, 3), stride=1).cuda()
        self.conv2 = nn.Conv2d(
            in_channels=32, out_channels=64, kernel_size=(3, 3), stride=1).cuda()

        self.conv3 = nn.Conv2d(
            in_channels=64, out_channels=128, kernel_size=(3, 3), stride=1).cuda()
        self.conv4 = nn.Conv2d(
            in_channels=128, out_channels=128, kernel_size=(3, 3), stride=1).cuda()

        self.conv5 = nn.Conv2d(
            in_channels=128, out_channels=256, kernel_size=(3, 3), stride=1).cuda()

        self.pool = nn.MaxPool2d(2, stride=2)

        self.FC1 = nn.Linear(256, 128).cuda()
        self.FC2 = nn.Linear(128, 128).cuda()
        self.FC3 = nn.Linear(128, 9).cuda()

        self.relu = nn.ReLU()

    def forward(self, x):

        x = x.float()
        x = self.relu(self.conv1(x))
        x = self.pool(self.relu(self.conv2(x)))

        x = self.relu(self.conv3(x))
        x = self.pool(self.relu(self.conv4(x)))

        x = self.relu(self.conv5(x))

        x = torch.nn.AvgPool2d(kernel_size=(
            27, 49), stride=0, padding=0, ceil_mode=False, count_include_pad=True)(x)

        x = x.squeeze()

        x = self.relu(self.FC1(x))
        x = self.relu(self.FC2(x))
        x = self.FC3(x)

        return x


def input_from_android(audio):
    model = CNN()
    model.load_state_dict(torch.load("model-combined-1.pth.tar"))
    model.cpu()
    audio = np.split(audio, [110250])
    audio = audio[0]
    librosa.output.write_wav('audio.wav', audio, 22050)
    audio = np.nan_to_num(audio)
    S = librosa.feature.melspectrogram(y=audio, n_mels=128, fmax=8000)
    melspec = librosa.power_to_db(S, ref=np.max)

    # if the input isnt of the specified order then you will get error in the reshape below
    melspec = melspec.reshape((1, 1, 128, 216))

    outputs = model(from_numpy(melspec))

    softmax = nn.Softmax()
    outputs = softmax(outputs)

    _, predicted = torch.max(outputs.data, 0)
    dict = {'0': 'Restaurant',
            '1': 'market',
            '2': 'Bus',
            '3': 'Road',
            '4': 'Factory',
            '5': 'Coffee_shop',
            '6': 'Subway',
            '7': 'Office',
            '8': 'bicycle',

            }
    predicted = predicted.detach().numpy()
    label = dict.get(str(predicted))
    return label, outputs.detach()


def classifyFromFile(filename):
    y, sr = librosa.load(path=filename, duration=5)
    label, result = input_from_android(y)
    values = [str("%.3f" % (i*100)) for i in result.numpy()]
    print(' '.join(values), label)
    return values, label


if __name__ == "__main__":
    classifyFromFile("0temp.wav")

    pass
    #y, sr = librosa.load(path="bicycle 91-8-new.wav", duration=5)

    # the input should be np.ndarray [shape=(n,)], n=110250 for 5 sec. eg(110250,)
    # print(input_from_android(y))

    # the index of the array is the class and the data is the confidency in percentage
    # 0=Restaurant
    # 1=market
    # 2=Bus
    # 3=Road
    # 4=Factory
    # 5=Coffee_shop
    # 6=Subway
    # 7=Office
    # 8=bicycle
