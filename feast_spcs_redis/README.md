# feast_spcs_redis

## 1.) Setup Snowflake Objects

All of the SQL code we will run can be found in ```feast_spcs_redis/spcs/sql```

```sql
CREATE OR REPLACE DATABASE feast_spcs_redis;
DROP SCHEMA PUBLIC;
CREATE OR REPLACE SCHEMA feature_store;
CREATE OR REPLACE IMAGE REPOSITORY feast_spcs_redis_image;
CREATE OR REPLACE STAGE feast_spcs_redis_stage
    ENCRYPTION = (TYPE = 'SNOWFLAKE_SSE');

CREATE COMPUTE POOL feast_spcs_redis
MIN_NODES = 1 --we will guarantee you this
MAX_NODES = 5 --we will take you up to this max
INSTANCE_FAMILY = HIGHMEM_X64_M --32cpu 256ram
AUTO_RESUME = TRUE
AUTO_SUSPEND_SECS = 1000000;
```

## 2.) Build Docker Images and Push

All of the Dockerfile code we will run can be found in ```feast_spcs_redis/spcs/docker```

Replace ```{snowflake_url}``` with you Snowflake Account URL

```feast_spcs_redis/spcs/docker/feast``` will create the feast environment
```feast_spcs_redis/spcs/docker/vscode``` will give you a coding environment in a pod for you to interactively work in and debug.  
```docker pull --platform linux/amd64 redis``` will get you redis


```
docker build --platform linux/amd64 -t {snowflake_url}/feast_spcs_redis/feature_store/feast_spcs_redis_image/feast:v1 .
```  
```
docker build --platform linux/amd64 -t {snowflake_url}/feast_spcs_redis/feature_store/feast_spcs_redis_image/vscode:v1 .
``` 
```
docker build --platform linux/amd64 -t {snowflake_url}/feast_spcs_redis/feature_store/feast_spcs_redis_image/redis:v1 .
```  


```docker push {snowflake_url}/feast_spcs_redis/feature_store/feast_spcs_redis_image/feast:v1```  
```docker push snowflake_url}/feast_spcs_redis/feature_store/feast_spcs_redis_image/vscode:v1```  
```docker push {snowflake_url}/feast_spcs_redis/feature_store/feast_spcs_redis_image/redis:v1```  

## 3.) Update manifest.yaml

Found in ```feast_spcs_redis/spcs```, update all of the image names to match to images names you just pushed. Should only need to change the Snowflake Acccount URL

## 4.) Mirror Github Repo to Snowflake Stage

Use ```feast_spcs_redis/push_to_stage.py``` to mirror your repo to snowflake. Update the credentials to your own login credentials. We will pass in the password and execute the script like this: ``` python push_to_stage.py {your_password}```

## 5.) Run Service

All of the SQL code we will run can be found in ```feast_spcs_redis/spcs/sql``` ... you will need to create an ingress integration that ideal is open to the internet.

```sql
CREATE SERVICE feast_spcs_redis
IN COMPUTE POOL feast_spcs_redis
FROM @feast_spcs_redis_stage
SPECIFICATION_FILE='/spcs/manifest.yaml'
MIN_INSTANCES=1
MAX_INSTANCES=6
EXTERNAL_ACCESS_INTEGRATIONS = (OPEN_ACCESS_INTEGRATION);

CALL SYSTEM$GET_SERVICE_STATUS('FEAST_SPCS_REDIS');
CALL SYSTEM$GET_SERVICE_LOGS('FEAST_SPCS_REDIS', '0', 'feastserver', 1000);
CALL SYSTEM$GET_SERVICE_LOGS('FEAST_SPCS_REDIS', '0', 'redis', 1000);
CALL SYSTEM$GET_SERVICE_LOGS('FEAST_SPCS_REDIS', '0', 'vscode', 1000);

SHOW ENDPOINTS IN SERVICE feast_spcs_redis;
```

## 6.) Play with Feast

You now have a public endpoint to a vscode editor to start playing with feast. Use ```sudo su``` password ```p123``` to work in the terminal. Feast has been installed on python.

Look at ```feast_spcs_redis/examples/cute_mantis``` for an example project. (You will not have the data)

*It is very easily to build a feast project locally, then push the code using ```push_to_stage.py```. The code will automatically sync, you do not have to keep restarting your service.
