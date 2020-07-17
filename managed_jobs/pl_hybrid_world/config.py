# edit config.py with your configuration below
region = "us-west-1" # region for classical compute; make sure it is the same as the region for the bucket below
role = "arn:aws:iam::465542368797:role/AmazonBraketJobExecutionRole"
bucket = 'pennylane-mjas' # this is where your training script will be uploaded; make sure it contains a 'results' folder
bucket_key = "simulator-output" # This is where individual task results will be stored
