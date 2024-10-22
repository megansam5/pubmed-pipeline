# 🌐 Automated NLP Pubmed Normalization Pipeline

One of the challenges that arrise when collating research papers from various sources is the issue of inconsistent naming of organisations. This can occur when the same organisation is referred to by different names in different papers, making it difficult to accurately match and collate the data.

For example, some publications might include

_Harvard University_

while others might include

_Harvard Medical School_

however both of them refer to essentially the same medical institution.

This inconsistency in naming can also have an impact on the results of data analysis, as it can lead to errors in data aggregation and hinder the ability to accurately compare the findings of different studies.


## 📜 Project Overview

This project is a fully automated data normalization pipeline using various AWS services, with a specific focus on leveraging Natural Language Processing (NLP) techniques to standardize the naming of organizations and institutions. When a XML file is uploaded to an S3 bucket, this system processes the file to normalize the data, sending email notifications throughout the process, before uploading the cleaned data as a csv file to another S3 bucket.


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
