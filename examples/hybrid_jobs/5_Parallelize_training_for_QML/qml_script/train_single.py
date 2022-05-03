import os
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
from qml_script.model import DressedQNN

# Dataset
from qml_script.helper_funs import sonar_dataset, get_device



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
    
    torch.manual_seed(seed)
    np.random.seed(seed)
    

    ########## Dataset ##########
    train_dataset = sonar_dataset(ndata, input_dir)
    
    train_loader = torch.utils.data.DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=0,
        pin_memory=True,
    )

    
    ########## quantum model ##########
    qc_dev = get_device(nwires, device_string)
    qc_dev_name = qc_dev.short_name
    
    if qc_dev_name == "lightning.gpu":
        device = torch.device("cuda")
    else:
        device = torch.device("cpu")
    
    model = DressedQNN(qc_dev).to(device)

    optimizer = optim.Adam(model.parameters(), lr=lr)
    scheduler = StepLR(optimizer, step_size=1, gamma=gamma)

    
    ########## Optimization ##########
    for epoch in range(1, epochs + 1):
        loss_before = train(model, device, train_loader, optimizer, epoch)
        scheduler.step()
        
        # Log the loss before the update step as a metric
        log_metric(
            metric_name="Loss",
            value=loss_before,
            iteration_number=epoch,
        )
    
    torch.save(model.state_dict(), f"{output_dir}/test_local.pt")
    save_job_result({"last loss": float(loss_before.detach().cpu())})


        
def train(model, device, train_loader, optimizer, epoch):
    model.train()
    for batch_idx, (data, target) in enumerate(train_loader):
        data, target = data.to(device), target.to(device)

        optimizer.zero_grad()
        output = model(data)

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

        
if __name__ == "__main__":
    main()