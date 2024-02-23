# -*- coding: utf-8 -*-
"""Untitled15.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1aFYwed-wT4MZREfjkZ5C9mYMQ-bIIZrg
"""

import torch.nn.functional as F

class Decoder(nn.Module):
    def __init__(self, input_vector_length=16, input_capsules=3):
        super(Decoder, self).__init__()
        input_dim = input_vector_length * input_capsules

        self.linear_layers = nn.Sequential(
            nn.Linear(input_dim, 256),
            nn.ReLU(inplace=True),
            nn.Linear(256, 7 * 7 * 256),  # Adjusted for the size after deconvolutions
            nn.ReLU(inplace=True)
        )

        self.deconv_layers = nn.Sequential(
            nn.ConvTranspose2d(256, 128, kernel_size=7, stride=4, padding=2, output_padding=2),
            nn.ReLU(inplace=True),
            nn.ConvTranspose2d(128, 64, kernel_size=5, stride=4, padding=2, output_padding=0),
            nn.ReLU(inplace=True),
            nn.ConvTranspose2d(64, 3, kernel_size=3, stride=2, padding=2, output_padding=1),
            nn.Sigmoid()
        )

    def forward(self, x):
        classes = (x ** 2).sum(dim=-1) ** 0.5
        classes = F.softmax(classes, dim=-1)

        _, max_length_indices = classes.max(dim=1)

        sparse_matrix = torch.eye(num_classes)
        if TRAIN_ON_GPU:
            sparse_matrix = sparse_matrix.cuda()
        y = sparse_matrix.index_select(dim=0, index=max_length_indices.data)

        x = x * y[:, :, None]
        flattened_x = x.contiguous().view(x.size(0), -1)
        linear_output = self.linear_layers(flattened_x)

        # Adjust the shape for deconvolutions
        linear_output = linear_output.view(linear_output.size(0), 256, 7, 7)

        # Apply deconvolutions
        reconstructions = self.deconv_layers(linear_output)

        return reconstructions, y

class CapsuleNetwork(nn.Module):

    def __init__(self):
        super(CapsuleNetwork, self).__init__()
        self.conv_layer = ConvLayer()
        self.cbam = CBAM(32)
        self.primary_capsules = PrimaryCaps()
        self.digit_capsules = DigitCaps()
        self.decoder = Decoder()

    def forward(self, images):
        primary_caps_output = self.primary_capsules(self.conv_layer(images))
        caps_output = self.digit_capsules(primary_caps_output).squeeze().transpose(0,1)
        reconstructions, y = self.decoder(caps_output)
        return caps_output, reconstructions, y