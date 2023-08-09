##### final-project-twitter
# Dashboard Service of Sentiment Analysis on Researcher-specified Twitter Topics
Group Members: 
<br>. Emily Yeh: Set up Lambda Function streaming tweet search result on AWS via Tweepy package, Case Study on the key word "Abortion Rights" 
<br>. Fiona Lee: Create S3 buckets to store the tweet raw data and RDS db to store select tweet data including sentiment analysis results, chain user input and data into pipeline
<br>. Helen Yap: Set up Lambda function to perform sentiment analysis on tweets and upsert tweet data to RDS 
<br>. Yutai Li: Build the dashboard to analyze and visualize the descriptive statistics and sentiment classification results 

## Introduction
We propose a workflow for analyzing the sentiments surrounding user-specified topics on Twitter. We will first stream the Twitter API to the AWS services, and provide analytical data upon keyword queries. By conducting content analysis tasks such as sentiment classification on those tweet conversations and organizing the descriptive information on a dashboard, our pipeline could allow users to gain the insights of how a specified topic is led and discussed by opinion leaders. 

Given the vast growth in social media usage and reliance for news and information, developing a large-scale method to collect and analyze Twitter data as described above would help inform how users feel and perceive the information that can then potentially inform downstream decision-making behaviors. 

## Instructions
1. Prerequisite: prepare an AWS personal account.
2. Run the following line in command line to download this pipeline tool:
```
git clone https://github.com/lsc4ss-s22/final-project-twitter.git
```
3. Run the following line in command line to install all packages needed:
```
pip -r requirements.txt
```
4. To open the GUI and start using the pipeline, go into the 'final-project-twitter' folder and run the following line in command line:
```
cd api
python application.py
```
5. Open the GUI in browser by clicking the url in command line (most likely to be "http://127.0.0.1:5000"), or copy and paste it into a new browser window. 
6. Follow the instruction on GUI and start getting data!

* To run the pipeline step by step or customize with specific purposes, follow step 1 to 3 and run [database.ipynb](https://github.com/lsc4ss-s22/final-project-twitter/blob/main/database.ipynb).

## User Interface
Because the target users of our pipeline tool are social science researchers who may not have advanced knolwedge and skills or enough time to build up a whole pipeline including tweets scraping, data storage, sentiment analysis and visualization, we hope to incapsulate all technical details in a downlodable repository. By entering parameters for tweets data, the pipeline takes in user-specified requirements and scrapes the corresponding data for analysis. Users do not need to run any code or upload any files manually onto AWS; the only prerequisite on the user end is have an AWS personal account available, and by sending parameters into the pipeline, databases with tweets data and visualizations of tweets' sentiment are ready to be accessed. Social science researchers can thus work with large-scaled social media data even without sufficient computational resources and advanced skills. 

## Workflow
![workflow diagram](https://github.com/lsc4ss-s22/final-project-twitter/blob/main/twitter_workflow.png) 

## Deploying Tweet Data
Two possible ways of retrieving the latest twitter data:
1. [Tweepy](https://www.tweepy.org/): Python library for requesting the official Twitter API. The standard search API has limitation of getting up to 100 tweets in each request, and user authentification can only make 180 requests per 15 minitue window. Only the tweets from the last 7 days are aavaliable.
2. [Twint](https://github.com/twintproject/twint): Python library for fetching tweets without using API. Can get unlimited tweets without time constraint.

## Sentiment Analysis with AWS Comprehend
To keep as much of the pipeline as possible within the AWS ecosystem, we leveraged AWS Comprehend to perform sentiment analysis. Other benefits of AWS Comprehend include its affordability. For example, as described by AWS, it would only cost ~$6 to process 10,000 units of text data with 550 characters each [(See: AWS documentation)](https://aws.amazon.com/comprehend/pricing/). A research experiment comparing NLP packages from AWS, Google, IBM, and Microsoft also affirmed that AWS boasts relatively cheaper rates for sentiment analysis than the other three cloud computing services. Furthermore, the same experiemnt also found that the AWS Comprehend sentiment analysis package performed with the best median accuracy measured in the absolute
polarity offset (APO) [(Pallas,Staufer, Kuhlenkamp, 2020)](http://www.ise.tu-berlin.de/fileadmin/fg308/publications/2020/pallas-staufer-kuhlenkamp-ieee-big-data-cloud-nlp-accuracy-evaluation-preprint.pdf).


## Parallelization Design
The current pipeline leverages the 10 allowed invocations of Lambda functions to parallelize sentiment analysis and RDS upsert. A stepfunction is used to pass 10 batches of tweet data to the Lambda function carrying the boto3 client call to AWS Comprehend and RDS. Parallelism on sentiment analysis and writing into database allows a significant decrease in time; the shorter waiting time and the smaller possibility of timeout in processing twitter data are the main advantages of our parallelization design.

## Cloud Storage
Unlike local storages that take up space in disk, cloud databases free up local storage space and provide easy access to large amount of data. In this project, our choice of AWS S3 bucket allows a complete backup for twitter data used in the sentiment analysis, and thus users can always refer back to the raw data, conduct more analyses, and draw different conclusions from the same dataset. Our design of using RDS for processed tweets data enables quick query of sentiment analysis results, and downstream statistical analyses and visualization based on the processed data can be easily performed and customized for every user. With the cloud nature of these two databases, research that utilizes our pipeline tool is no more limited by the local computational resources and storage space; moreover, these databases in the AWS ecosystem prevent any incompatibility between our data processing pipeline and data storage. 

## Dashboard Interface
For visualization, our project use Amazon QuickSight to visualize the data collected from Twitter. QuickSight is an AWS built-in visualization tool that is scalable, serverless, embeddable and optimized for database cloud. In theory (without the restrictions of AWS Academy account), Amazon QuickSight can connect to a wide varity of locan and on-premises datasources, including Oracle, SQL server, and AWS sources like RDS, Redshift, Athena, and S3. QuickSight can also scale the analytics capabilities to hundreds or thousands of users by using "SPICE" -a Super-fast, Parallel, In-memory Calculation Engine. 

In our project, the data flows into a RDS database for quick query of sentiment analysis, and in theory the Amazon QuickSight is directly connected to the RDS through a same VPC id to enable concurrently data visualization as the data entered the RDS database. Due to the cloud nature of QuickSight, the scalability of QuickSight is also ensured to handle large data from RDS in timelessness fashion. 

Screenshots of the dashboard <br>
<img src="https://github.com/lsc4ss-s22/final-project-twitter/blob/main/dashboard/Screen%20Shot%202022-06-03%20at%2015.46.41.png?raw=true" width="800" height="400">


## Case Study: Abortion Rights
In a case study, we test our workflow by focusing on the discussion on abortion rights on Twitter. Specifically, we used the word "abortion" as the search term, and limit the date to June 2nd 2022. Through our scraping -> storing -> and visualization workflow, we collected 600 tweets for that single day in total. The overall sentiment is overly negative, with only a few tweets have the positive sentiment. Also, the number of likes and retweets are highly correlated, meaning that both variables are good indicators of the influences of tweets. However, in the topic of abortion, the sentiment score is not strongly correlated with neither number of likes and number of retweets. This visualization tool generate insights for users to quickly catch the overall sentiment of one topic on Twitter.
<img src="https://github.com/lsc4ss-s22/final-project-twitter/blob/main/dashboard/Screen%20Shot%202022-06-03%20at%2015.47.19.png?raw=true" width="1000" height="400">
<img src="https://github.com/lsc4ss-s22/final-project-twitter/blob/main/dashboard/Screen%20Shot%202022-06-03%20at%2015.49.17.png?raw=true" width="1000" height="400">


## Prospects of scalability
Our data pipeline is scalable on multiple fronts: 

* **Lambda functions:** We are currently limited to 10 invocations of Lambda by AWS Academy. To scale up to potentially 10,000 Lambda functions, we recommend switching to a personal AWS account, which can provide more resources for larger-scale parallelization.

* **RDS:** If greater storage capacity is needed, it is possible to modify the instance type of the current RDS db. If there is uncertainty regarding future workload size, it is also possible to set RDS to automatically scale. 

* **QuickSight:** QuickSight is serverless and is built with "SPICE" – a super-fast, parallel, in-memory calculation engine that is designed to handle large data and enables hundreds of users to access the dashboard simutaneously. 




## References
* https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-throughput-horizontal-scaling-and-batching.html 
* https://aws.amazon.com/blogs/database/scaling-your-amazon-rds-instance-vertically-and-horizontally/
* http://www.ise.tu-berlin.de/fileadmin/fg308/publications/2020/pallas-staufer-kuhlenkamp-ieee-big-data-cloud-nlp-accuracy-evaluation-preprint.pdf
* https://aws.amazon.com/comprehend/pricing/

