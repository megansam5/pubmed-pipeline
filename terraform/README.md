# ☁️ Cloud Deployment using Terraform

The project is designed to be deployed on the cloud using AWS services via terraform. Assuming some prerequisite setup explained in this document, the cloud infrastructure can be deployed using a single command. When a new xml file is added into the folder in the bucket with the name: `DISEASE_NAME_dd-mm-yy.xml`, you will get emailed to let you know the process has begun, and then another email once the cleaned csv file is uploaded to the output file.

## 🛠️ Prerequisites
- **Terraform** installed
- **AWS CLI** downloaded
- **AWS ECR** repository for the pipeline image
- Provision an **AWS S3** input bucket
- provision an **AWS S3** output bucket
- Read the Prequrequisites and Setup section of the following READMEs (setup and upload images to ECR repositories):
    - [pipeline/README.md](../pipeline/README.md)

## ⚙️ Setup
1. Install AWS CLI for your machine by following the link: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html and run the command:
    ```bash
    aws configure
    ```
    Follow the prompts to enter your AWS credentials.

2. Create `terraform.tfvars` file and fill with the following variables
    ```bash
    # AWS Credentials
    AWS_ACCESS_KEY        = "your-aws-access-key"
    AWS_SECRET_ACCESS_KEY = "your-aws-secret-key"
    ACCOUNT_ID            = "your-aws-account-id"

    # AWS Region and Network Config
    REGION                = "the-aws-region"
    SUBNET_ID             = "the-subnet-id"
    SECURITY_GROUP_ID     = "the-security-group-id"

    # S3 Bucket Name
    INPUT_BUCKET_NAME        = "name-of-input-S3-bucket"
    OUTPUT_BUCKET_NAME       = "name-of-input-S3-bucket"
    FOLDER_NAME              = "name-of-folder-in-input-bucket"

    # ECR Repositories
    PIPELINE_ECR_REPO       = "ecr-repo-name-for-pipeline"

    # Email Configuration
    FROM_ADDRESS            = "address-to-send-emails-from"
    TO_ADDRESS              = "address-to-send-emails-to"
    ```

3. Initialise terraform:
    ```bash
    terraform init
    ```

4. Deploy cloud services:
    ```bash
    terraform apply
    ```
    - Enter yes when it asks to approve changes.
    - Can be used to redeploy if resource definitions have been changed.

5. To bring down the cloud infrastructure:
    ```bash
    terraform destroy
    ```
    - To recreate start again from step 3.

## 📝 Notes

- Remember to add any `*.env`, `*.tfvars`, `*.pem`, `*.pemkey` files to gitignore if not already listed.