# Tutorial that I followed to dockerize the application

https://www.youtube.com/watch?v=NU406wZz1eU

## Steps to host the docker container into the cloud

I used [Amazon ECR](https://us-east-1.console.aws.amazon.com/ecr/public-registry/repositories?region=us-east-1) to host the docker container. The public repository where the container is located is named whisperx-api-ecr. Lastly, I pushed the lastest docker image into the ECR repository using the push commands specified on the repository.

Then I launched an EC2 instance named [Whisperx API](https://us-east-1.console.aws.amazon.com/ec2/home?region=us-east-1#InstanceDetails:instanceId=i-06c5cf0570e8376a7). I then installed docker into this instance and then pulled the docker image like `docker pull public.ecr.aws/w6h5n5v7/whisperx-api-ecr:latest` to EC2 from ECR.

`Make sure that your local machine architecture (x86 or arm64) matches the architecture of the machine where you are going to run the docker container from the built image. E.g. - If you have an Apple M1 machine then make sure the EC2 instance has an arm64 architecture when you set it up, or else the container won't run.`

Lastly, after the docker image has been pulled, I run the container using `docker run -d -p 5001:5001 public.ecr.aws/w6h5n5v7/whisperx-api-ecr:latest`. The d flag specifies detached mode to run the container and the p flag specifies the port number pairing.

Now you can call the API by calling `http://ec2-54-82-24-182.compute-1.amazonaws.com:5001/transcribe?bucket_id={bucket}&project_id={project}&user_id={user}`
