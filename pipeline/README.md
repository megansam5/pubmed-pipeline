# Pudmed Data Match

## Set up (inside pipeline folder)
1. Activate a virtual environment
2. Install dependencies with `pip install -r requirements.txt`
3. Download the smallest spacy model with `python3 -m spacy download en_core_web_sm`
4. Create a `.env` file with the following:
```
AWS_ACCESS_KEY=XXX
AWS_SECRET_ACCESS_KEY=XXXX
INPUT_BUCKET_NAME=XXX
OUTPUT_BUCKET_NAME=XXX
FOLDER_NAME=XX
```

## Running locally
Run the pipeline with `python3 pipeline.py`
- This will print out all the times.

## Running on a Docker File
- Run `docker build -t IMAGE_NAME .` to create the docker image.
- Run `docker run --env-file .env IMAGE_NAME` to run the image.


## Creating and pushing Docker file to ECR
- Authenticate docker with `aws ecr get-login-password --region YOUR_AWS_REGION | docker login --username AWS --password-stdin YOUR_AWS_ACCOUNT_ID.dkr.ecr.YOUR_AWS_REGION.amazonaws.com`
- Create an ECR repository with `aws ecr create-repository --repository-name YOUR_REPOSITORY_NAME --region YOUR_AWS_REGION`
- Build the image with the correct platform with `docker build -t YOUR_IMAGE_NAME . --platform "linux/amd64"`
- Tag the image with `docker tag YOUR_IMAGE_NAME:latest YOUR_AWS_ACCOUNT_ID.dkr.ecr.YOUR_AWS_REGION.amazonaws.com/YOUR_REPOSITORY_NAME:latest`
- Push the image to the ECR with `docker push YOUR_AWS_ACCOUNT_ID.dkr.ecr.YOUR_AWS_REGION.amazonaws.com/YOUR_REPOSITORY_NAME:latest`d

## Next steps
Move into the terraform folder to create the AWS services, using `cd ../terraform`


## Comparing Different Similarity Techniques

#### Jaro.normalized_similarity (score_cutoff=0.9)
- Time: 311.92 s 
- % Institutes matched: 52.41%

#### DamerauLevenshtein.normalized_similarity (score_cutoff=0.9)
- Time: 1186.27 s 
- % Institutes matched: 42.23%

#### Hamming.normalized_similarity (score_cutoff=0.9)
- Time: 300.65 s 
- % Institutes matched: 39.95%

#### partial_ratio (score_cutoff=90) <--- chosen
- Time: 609.09 s (10.15 mins)
- % Institutes matched: **86.26%**

### Now with added pandarallel for parallel processing
- 167.70 s (2.8 mins)