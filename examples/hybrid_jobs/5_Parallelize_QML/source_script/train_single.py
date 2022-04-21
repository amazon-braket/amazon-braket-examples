import os
import time
import numpy as np
import json
import pennylane as qml

from braket.jobs import save_job_result
from braket.jobs.metrics import log_metric

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.optim.lr_scheduler import StepLR

# Network definition
from source_script.model_def import DressedQNN

# Dataset
from source_script.helper_funs import sonar_dataset, random_dataset, get_device



def main():
    input_dir = os.environ["AMZN_BRAKET_INPUT_DIR"]  
    output_dir = os.environ["AMZN_BRAKET_JOB_RESULTS_DIR"]
    hp_file = os.environ["AMZN_BRAKET_HP_FILE"]
    device_string = os.environ["AMZN_BRAKET_DEVICE_ARN"]
    
    ########## Hyperparameters ##########
    with open(hp_file, "r") as f:
        hyperparams = json.load(f)
    print("hyperparams: ", hyperparams)
    
    nwires = int(hyperparams["nwires"])
    ndata = int(hyperparams["ndata"])
    batch_size = int(hyperparams["batch_size"])
    epochs = int(hyperparams["epochs"])

    gamma = float(hyperparams["gamma"])
    lr = float(hyperparams["lr"])
        
    seed = int(hyperparams["seed"])
    to_eval = int(hyperparams["to_eval"])
    
    torch.manual_seed(seed)
    np.random.seed(seed)
    
#     print("nwires", nwires)
#     print("ndata", ndata)
#     print("batch_size", batch_size)
#     print("epochs", epochs)
#     print("gamma", gamma)
#     print("lr", lr)
#     print("seed", seed)
#     print("to_eval", to_eval)
#     print("qc_dev_name", qc_dev_name)
    

    ########## Dataset ##########
#     train_dataset = random_dataset(ndata)
    train_dataset = sonar_dataset(ndata, input_dir)
    # train_dataset = cancer_dataset()
    
    train_loader = torch.utils.data.DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=0,
        pin_memory=True,
    )

    
    ########## quantum model ##########
    qc_dev = get_device(nwires, device_string)
    # qc_dev = qml.device(qc_dev_name, wires=nwires)
    qc_dev_name = qc_dev.short_name
    
    if qc_dev_name=="lightning.gpu":
        device = torch.device("cuda")
    else:
        device = torch.device("cpu")
    
    model = DressedQNN(qc_dev).to(device)

    optimizer = optim.Adam(model.parameters(), lr=lr)
    scheduler = StepLR(optimizer, step_size=1, gamma=gamma)

    
    ########## Optimization ##########
    start = time.time()
    for epoch in range(1, epochs + 1):
        loss_before = train(model, device, train_loader, optimizer, epoch)
        scheduler.step()
        
        # Log the loss before the update step as a metric
        log_metric(
            metric_name="Loss",
            value=loss_before,
            iteration_number=epoch,
        )

    elapsed = time.time()-start
    print('elapsed time: ', elapsed)
    
    torch.save(model.state_dict(), f"{output_dir}/test_local.pt")
    save_job_result({"last loss": float(loss_before.detach().cpu())})
    
    
    ########## Accuracy Evaluation (optional) ##########
    if to_eval:
        eval_loader = torch.utils.data.DataLoader(
            train_dataset,
            batch_size=ndata,
            shuffle=True,
            num_workers=0,
            pin_memory=True,
        )
        accuracy = eval_accuracy(model, device, eval_loader)
        print("accuracy: ", accuracy)
        save_job_result({"accuracy": accuracy})


        
def train(model, device, train_loader, optimizer, epoch):
    model.train()
    for batch_idx, (data, target) in enumerate(train_loader):
        data, target = data.to(device), target.to(device)

        optimizer.zero_grad()
        output = model(data)
#         print(output.shape)
#         print(target.shape)

        # loss = F.nll_loss(output, target)
        # loss = F.hinge_embedding_loss(output, target, margin=0.0)
        loss = F.margin_ranking_loss(output, torch.zeros_like(output), target, margin=0.1)
        
        loss.backward()
        optimizer.step()
        print(
            "Train Epoch: {} [{}/{} ({:.0f}%)]\tLoss: {:.6f}".format(
                epoch,
                batch_idx * len(data),
                len(train_loader.dataset),
                100.0 * batch_idx / len(train_loader),
                loss.item(),
            )
        )
        
    return loss


def eval_accuracy(model, device, eval_loader):
    model.eval()
    correct = 0
    # with torch.no_grad():
    for batch_idx, (data, target) in enumerate(eval_loader):
        data, target = data.to(device), target.to(device)
        output = model(data)

        pred = torch.where(output>=0, +1, -1)
        pred = pred.to(device)
        # print("pred ", pred)
        # print("target ", target)
        print("data size: ", len(eval_loader.dataset))

        correct += pred.eq(target.view_as(pred)).sum().item()
        print("correct predictions: ", correct)

    accuracy = correct / len(eval_loader.dataset)

    return accuracy
        
        


if __name__ == "__main__":
    try:
        main()
        print("Training Successful!!")
    except BaseException as e:
        print(e)
        print("Training Fails...")


