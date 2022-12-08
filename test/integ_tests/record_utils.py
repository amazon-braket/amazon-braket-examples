import boto3
import json
import braket.aws

recording = True


class BraketClientWrapper():
    def __init__(self, braket_client):
        self.__class__ = type(
            braket_client.__class__.__name__,
            (self.__class__, braket_client.__class__),
            {}
        )
        self.__dict__ = braket_client.__dict__
        self.braket_client = braket_client
        self.num_get_device_calls = 0
        self.num_create_task_calls = 0
        self.num_get_task_calls = 0

    def get_device(self, deviceArn):
        if recording:
            result = self.braket_client.get_device(deviceArn=deviceArn)
            with open(f"get_device_results_{self.num_get_device_calls}.json", "w") as f:
                json.dump(result, f, indent=2)
        else:
            with open(f"get_device_results_{self.num_get_device_calls}.json", "r") as f:
                result = json.load(f)
        self.num_get_device_calls += 1
        return result

    def create_quantum_task(self, **kwargs):
        if recording:
            result = self.braket_client.create_quantum_task(**kwargs)
            with open(f"create_task_results_{self.num_create_task_calls}.json", "w") as f:
                json.dump(result, f, indent=2)
        else:
            with open(f"create_task_results_{self.num_create_task_calls}.json", "r") as f:
                result = json.load(f)
        self.num_create_task_calls += 1
        return result

    def get_quantum_task(self, quantumTaskArn):
        if recording:
            result = self.braket_client.get_quantum_task(quantumTaskArn=quantumTaskArn)
            with open(f"get_task_results_{self.num_get_task_calls}.json", "w") as f:
                json.dump(result, f, indent=2, default=str)
            if result["status"] in braket.aws.aws_quantum_task.AwsQuantumTask.TERMINAL_STATES:
                # There is not need to record every time we poll.
                self.num_get_task_calls += 1
        else:
            with open(f"get_task_results_{self.num_get_task_calls}.json", "r") as f:
                result = json.load(f)
            self.num_get_task_calls += 1
        return result


class Recorder(boto3.Session):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def client(self, *args, **kwargs):
        boto_client = super().client(*args, **kwargs)
        if args and args[0] == "braket" or kwargs and "service_name" in kwargs and kwargs["service_name"] == "braket":
            return BraketClientWrapper(boto_client)
        return boto_client


real_retrieve_s3_object_body = braket.aws.aws_session.AwsSession.retrieve_s3_object_body
num_s3_results = 0


class AwsSessionWrapper():
    def retrieve_s3_object_body(self, s3_bucket, s3_object_key):
        global num_s3_results
        if recording:
            result = real_retrieve_s3_object_body(self, s3_bucket, s3_object_key)
            with open(f"from_s3_results_{num_s3_results}.json", "w") as f:
                json.dump(json.loads(result), f, indent=2)
        else:
            with open(f"from_s3_results_{num_s3_results}.json", "r") as f:
                result = f.read()
        num_s3_results += 1
        return result


boto3.Session = Recorder
braket.aws.aws_session.AwsSession.retrieve_s3_object_body = AwsSessionWrapper.retrieve_s3_object_body


def record():
    global recording
    recording = True


def playback():
    global recording
    recording = False
