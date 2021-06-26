# ArchiveSpark on Docker Experiments
1. Get data from Common Crawl
2. Process file
3. Upload result to a S3 bucket

## Requirements
* [Docker](https://www.docker.com/get-docker)
  
## Usage
### Run Docker image from Docker Hub
```
docker run --env-file env.list --rm -ti yinlinchen/archivespark:latest
```

### Docker Environment
| Key | Value | 
| ------------- | ------------- | 
| `WARC_FILENAME` | WARC FILENAE | 
| `WARC_URL` | WARC URL | 

* Example:[env.list](env.list)

## Build Docker image locally
```
docker build -t="archivespark:latest" .
```

## Run Docker image locally commands
```
# Run docker image with env file
docker run --env-file env.list --rm -ti archivespark:latest 

# Example 1
docker run --env-file env.list --rm -ti -v /home/ec2-user/config:/config archivespark:latest

# Example 2
docker run --env-file env.list --rm -ti -v /home/ec2-user/config:/config -v /home/ec2-user/notebooks:/notebooks -v /home/ec2-user/data:/data -v /home/ec2-user/results:/results archivespark:latest
```