# 🌐 Automated NLP Pubmed Normalization Pipeline

## 📜 Project Overview

This project implements a fully automated data normalization pipeline using various AWS services, with a specific focus on leveraging Natural Language Processing (NLP) techniques. The system is designed to streamline the workflow of uploading XML files to an S3 bucket, processing those files to normalize the data, and sending email notifications throughout the process. 

## 🛠️ Tools & Technologies

- **AWS Services**: 
  - **S3**: Used for storing input XML files and output CSV files.
  - **ECS**: Executes containerized tasks that implement NLP techniques for data normalization.
  - **SES**: Sends email notifications before and after processing to keep stakeholders informed.
  - **Step Functions**: Orchestrates the sequence of operations, ensuring the proper flow of tasks.

- **NLP Tools**:
  - **spaCy**: A powerful NLP library used for tasks like tokenization, named entity recognition, and linguistic annotations.
  - **RapidFuzz**: A fuzzy string matching library that helps in identifying similarities and discrepancies in text data.
  - **pandarallel**: A tool for parallelizing operations in Pandas, significantly improving performance by enabling multiprocessing during data normalization.

- **Terraform**: 
  - Infrastructure as Code tool used for provisioning and managing AWS resources, ensuring a reproducible and scalable architecture.

- **AWS CLI**: Command-line interface for interacting with AWS services and managing resources.

## 🛠️ Installation and Setup

To correctly set up this project and deploy it to the cloud, please follow the instructions detailed in the [terraform folder README.md](./terraform/README.md).
