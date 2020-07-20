# edit this config file with your configuration below
region = "us-west-1"
# insert your 12-digit AWS account ID below into role
role = "arn:aws:iam::465542368797:role/AmazonBraketJobExecutionRole" # This is execution role that allows Amazon Braket to perform actions on your behalf
bucket = 'hybrid-job-mjas' # This is where your training script will be uploaded; make sure this bucket is in the region set above
bucket_key = "hybrid-output" # This is where individual task results will be stored
