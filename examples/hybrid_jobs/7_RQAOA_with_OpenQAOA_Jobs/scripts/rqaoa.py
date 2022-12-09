# Note:
# These imports need to be resolved **whithin** the aws docker. Not in this folder! :) 

from openqaoa.workflows.managed_jobs import AWSJobs
from braket.jobs import save_job_result
import json


def main():
    """
    The entry point is kept clean and simple and all the load statements are hidden in the `aws_jobs_load` function (which will become part of the OpenQAOA library)
    """

    job = AWSJobs(algorithm='RQAOA')
    job.load_input_data()
    job.set_up()
    job.run_workflow()
    
    print('keys', job.workflow.results.keys())
    
    save_job_result({"rqaoa_result": job.workflow.results.as_dict()})
    

if __name__ == "__main__":
    main()