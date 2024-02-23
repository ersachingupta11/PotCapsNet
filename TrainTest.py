# -*- coding: utf-8 -*-
"""Untitled15.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1aFYwed-wT4MZREfjkZ5C9mYMQ-bIIZrg
"""

def train(capsule_net, criterion, optimizer, train_loader, val_loader, n_epochs, print_every=80):
    train_losses = []
    train_accuracies = []
    val_losses = []
    val_accuracies = []

    for epoch in range(1, n_epochs + 1):

        train_loss = 0.0
        train_correct = 0
        train_total = 0

        capsule_net.train()

        for batch_i, (images, targets) in enumerate(train_loader):

            targets = torch.eye(num_classes).index_select(dim=0, index=targets)

            if TRAIN_ON_GPU:
                images, targets = images.to(device), targets.to(device)

            optimizer.zero_grad()

            caps_output, reconstructions, y = capsule_net(images)

            loss = criterion(caps_output, targets, images, reconstructions)

            loss.backward()
            optimizer.step()

            train_loss += loss.item()

            _, predicted = torch.max(y.data, 1)
            train_total += targets.size(0)
            train_correct += (predicted == targets.argmax(dim=1)).sum().item()

            if batch_i != 0 and batch_i % print_every == 0:
                avg_train_loss = train_loss / print_every
                avg_train_accuracy = 100.0 * train_correct / train_total
                train_losses.append(avg_train_loss)
                train_accuracies.append(avg_train_accuracy)
                print('Epoch: {}\tBatch: {}\tTraining Loss: {:.8f}\tTraining Accuracy: {:.2f}%'.format(
                    epoch, batch_i, avg_train_loss, avg_train_accuracy))
                train_loss = 0
                train_correct = 0
                train_total = 0

        val_loss = 0.0
        val_correct = 0
        val_total = 0

        capsule_net.eval()

        with torch.no_grad():
            for images, targets in val_loader:
                targets = torch.eye(num_classes).index_select(dim=0, index=targets)

                if TRAIN_ON_GPU:
                    images, targets = images.to(device), targets.to(device)

                caps_output, reconstructions, y = capsule_net(images)

                loss = criterion(caps_output, targets, images, reconstructions)

                val_loss += loss.item()

                _, predicted = torch.max(y.data, 1)
                val_total += targets.size(0)
                val_correct += (predicted == targets.argmax(dim=1)).sum().item()

        avg_val_loss = val_loss / len(val_loader)
        avg_val_accuracy = 100.0 * val_correct / val_total
        val_losses.append(avg_val_loss)
        val_accuracies.append(avg_val_accuracy)
        print('Epoch: {}\tValidation Loss: {:.8f}\tValidation Accuracy: {:.2f}%'.format(
            epoch, avg_val_loss, avg_val_accuracy))

    return train_losses, train_accuracies, val_losses, val_accuracies

def test(capsule_net, test_loader):
    class_correct = list(0. for i in range(num_classes))
    class_total = list(0. for i in range(num_classes))

    test_loss = 0

    capsule_net.eval()

    for batch_i, (images, target) in enumerate(test_loader):
        target = torch.eye(num_classes).index_select(dim=0, index=target)

        batch_size = images.size(0)

        if TRAIN_ON_GPU:
            images, target = images.cuda(), target.cuda()

        caps_output, reconstructions, y = capsule_net(images)
        loss = criterion(caps_output, target, images, reconstructions)
        test_loss += loss.item()
        _, pred = torch.max(y.data.cpu(), 1)
        _, target_shape = torch.max(target.data.cpu(), 1)

        correct = np.squeeze(pred.eq(target_shape.data.view_as(pred)))
        for i in range(batch_size):
            label = target_shape.data[i]
            class_correct[label] += correct[i].item()
            class_total[label] += 1

    avg_test_loss = test_loss/len(test_loader)
    print('Test Loss: {:.8f}\n'.format(avg_test_loss))

    for i in range(num_classes):
        if class_total[i] > 0:
            print('Test Accuracy of %5s: %2d%% (%2d/%2d)' % (
                str(i), 100 * class_correct[i] / class_total[i],
                np.sum(class_correct[i]), np.sum(class_total[i])))
        else:
            print('Test Accuracy of %5s: N/A (no training examples)' % (str(i)))

    print('\nTest Accuracy (Overall): %2d%% (%2d/%2d)' % (
        100. * np.sum(class_correct) / np.sum(class_total),
        np.sum(class_correct), np.sum(class_total)))

    return caps_output, images, reconstructions

n_epochs = 100
train_losses, train_accuracies, val_losses, val_accuracies = train(capsule_net, criterion, optimizer, trainloader, validloader, n_epochs=n_epochs)

def plot_losses(train_losses, val_losses):
    plt.plot(train_losses, label='Training Loss')
    plt.plot(val_losses, label='Validation Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.title('Training and Validation Loss')
    plt.legend()
    plt.show()

def plot_accuracies(train_accuracies, val_accuracies):
    plt.plot(train_accuracies, label='Training Accuracy')
    plt.plot(val_accuracies, label='Validation Accuracy')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy (%)')
    plt.title('Training and Validation Accuracy')
    plt.legend()
    plt.show()

plot_losses(train_losses, val_losses)

plot_accuracies(train_accuracies, val_accuracies)

print("Test")
caps_output, images, reconstructions = test(capsule_net, testloader)

print("Testing on Trainloader")
caps_output, images, reconstructions = test(capsule_net, trainloader)



