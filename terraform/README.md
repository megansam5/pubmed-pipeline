# Terraforming

## Set-up

- Create a `terraform.tfvars` file with the following:
```
AWS_ACCESS_KEY = "XXX"
AWS_SECRET_ACCESS_KEY = "XXXj"
INPUT_BUCKET_NAME= "XXX"
OUTPUT_BUCKET_NAME = "XXX"
FOLDER_NAME = "XXX"
FROM_ADDRESS = "XXX"
TO_ADDRESS = "XXX"
SUBNET_ID = "XXX"
SECURITY_GROUP_ID = "XXX"
ACCOUNT_ID = "XXX"
```


## Running

- Check that there are no errors with `terraform plan`
- Create all AWS services with `terraform apply'


Now when a new xml file is added into the folder in the bucket with the name: `DISEASE_NAME_dd-mm-yy.xml`, you will get emailed to let you know the process has begun, and then another email once the cleaned csv file is uploaded to the output file.

- Remember to `terraform destroy` when you are done!