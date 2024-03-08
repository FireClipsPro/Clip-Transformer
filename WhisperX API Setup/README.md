# Tutorial that I followed to dockerize the application

https://www.youtube.com/watch?v=NU406wZz1eU

## Steps to host the docker container into the cloud

I used [Amazon ECR](https://us-east-1.console.aws.amazon.com/ecr/private-registry/repositories?region=us-east-1) to host the docker container. The repository where the container is located is named transcriber_ecr.

Then I launched an EC2 instance named [Whisperx API](https://us-east-1.console.aws.amazon.com/ec2/home?region=us-east-1#InstanceDetails:instanceId=i-06c5cf0570e8376a7). I then installed docker into this instance to and then pulled the docker image from ECR to run it locally.

`Make sure that your local machine architecture (x86 or arm64) makes the architecture of the machine where you are going to run the docker container from the built image. E.g. - If you have an Apple M1 machine then make sure the EC2 instance has a arm64 architecture when you set it up, or else the container won't run.`

Lastly, after the docker image has been pulled, I run the container using `docker run -d -p 8000:8000 public.ecr.aws/w6h5n5v7/whisperx-api-ecr:latest`. The d flag specifies detached mode to run the container and the p flag specifies the post number pairing.
