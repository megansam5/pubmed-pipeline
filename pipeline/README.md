# Pudmed Data Match

## 🌟 Overview

The **Pipeline** component of this project is designed to automate the normalization of XML data files uploaded to an S3 bucket. Utilizing Natural Language Processing (NLP) techniques, the system processes incoming XML files to extract and normalize relevant information, ensuring that the data is consistent and ready for further analysis.This task leverages powerful NLP tools like **spaCy** for natural language understanding, **RapidFuzz** for fuzzy string matching and similarity calculations, and **pandarallel** for efficient multiprocessing, ensuring that data normalization is fast and scalable.


## 🔍 Folder Structure

- `Dockerfile`: Docker configuration for the project
- `dockerise.sh`: Shell script to build and push Docker image to AWS ECR
- `extract.py`: Extracts XML file from S3
- `transform.py`: Cleans and transforms the extracted data
- `load.py`: Loads the transformed data into another S3 bucket
- `pipeline.py`: Main ETL pipeline script that orchestrates the workflow
- `requirements.txt`: Required Python packages

## 🛠️ Prerequisites
- **Docker** installed.
- Setup **ECR** repository to store analyser pipeline docker image.  
- If no **ECR** then create one with:
```
aws ecr get-login-password --region eu-west-2 | docker login --username AWS --password-stdin <YOUR_ECR_REGISTRY_ID>.dkr.ecr.eu-west-2.amazonaws.com
aws ecr create-repository --repository-name <ECR_REP_NAME> --region eu-west-2
```

Optional:
- **Python** installed (For running locally)

## ⚙️ Setup 
Create a `.env` file and fill with the following variables
```bash
# AWS Configuration
AWS_ACCESS_KEY=<your_aws_access_key>
AWS_SECRET_ACCESS_KEY=<your_aws_secret_access_key>


# S3 Bucket Configuration
BUCKET_NAME=<s3_bucket_name>
INPUT_BUCKET_NAME=<s3_input_bucket_name>
OUTPUT_BUCKET_NAME=<s3_output_bucket_name>
FOLDER_NAME=<folder_name_in_s3_input_bucket>

# ECR Configuration
ECR_REGISTRY_ID=<id_of_ecr_repo_to_store_image>
ECR_REPO_NAME=<name_of_ecr_repo_to_store_image>
IMAGE_NAME=<docker_image_name>
```

### ☁️ Pushing to the Cloud
To deploy the overall cloud infrastructure the pipeline must be containerised and hosted on the cloud:

1. Make sure you have the Docker application running in the background
2. Dockerise and upload the application:
    ```bash
    bash dockerise.sh
    ```
    This will:
    - Authenticate your aws credentials with docker
    - Create the docker image
    - Tag the docker image
    - Upload tagged image to the ECR repository

### 💻 Running Locally (MacOS, **Optional**)
The pipeline can also be ran locally by:

1. Creating and activating virtual environment:
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```
2. Install requirements:
    ```bash
    pip install -r requirements.txt
    ```
3. Download the smallest spacy model:
    ```bash
    python3 -m spacy download en_core_web_sm
    ```
4. Running the pipeline:
    ```bash
    python3 pipeline.py
    ```


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
