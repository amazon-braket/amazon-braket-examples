import torch
import numpy as np
import os
import csv
import pennylane as qml


def read_csv_raw(fname):
    data = []
    with open(fname) as csvfile:
        readCSV = csv.reader(csvfile)
        for row in readCSV:
            data.append([r for r in row])

    return data


class Dataset(torch.utils.data.Dataset):
  'Characterizes a dataset for PyTorch'
  def __init__(self, data, label):
        'Initialization'
        self.data = data
        self.label = label

  def __len__(self):
        'Denotes the total number of samples'
        return len(self.label)

  def __getitem__(self, index):
        'Generates one sample of data'
        # Load data and get label
        x = self.data[index]
        y = self.label[index]
        return x, y


def sonar_dataset(ndata, input_dir):  
      raw_data = read_csv_raw(f"{input_dir}/input-data/sonar.all-data")
      data = []
      label = []
      for data_point in raw_data:
            data.append([float(element) for element in data_point[0:-1]])
            one_label = 1 if data_point[-1]=="M" else -1
            label.append(one_label)

      idx = np.random.permutation(208)
      data = np.array(data)[idx[0:ndata]].astype('float32')
      label = np.array(label)[idx[0:ndata]].astype('float32')

      train_dataset = Dataset(data=data, label=label)

      return train_dataset

    
def get_device(n_wires, device_string):
    device_prefix = device_string.split(":")[0]

    if device_prefix=="local":
        prefix, device_name = device_string.split("/")
        device = qml.device(device_name, wires=n_wires)
        print("Using local simulator: ", device.name)
    else:
        device = qml.device('braket.aws.qubit', 
                             device_arn=device_string, 
                             s3_destination_folder=None,
                             wires=n_wires,
                             parallel=True,
                             max_parallel=30)
        print("Using AWS managed device: ", device.name)
        
    return device