# BlueBird
BlueBird can duplicate a thread in a popular social media and re-post the same content.

Unfortunately will work only with posts from the last seven days.
## Requirements  
- Python 3.8
- [API authentication credentials](https://developer.twitter.com/)

## Setup
Edit the file [.env](config%2F.env) whith your authentication credentials

Your App permissions need to be Read and write

Please do not open Issues asking for help how to config your api in the social media, there is a lot of tutorials about.

```bash 
bearer_token="your-bearer-token"
consumer_key="your-consumer-key"
consumer_secret="your-consumer-secret"
access_token="your-access-token"
access_token_secret="your-access-token-secret"
client_id="your-client-id"
client_secret="your-client-secret"
``` 


## Installation  
1. Clone the repo: 
	```bash 
	git clone https://github.com/harrypython/BlueBird.git
	cd BlueBird 
	```  
1. Install the requirements: 
	```bash 
	pip install -r requirements.txt
	```  

## Get started  
1. Duplicate the post https://twitter.com/BarackObama/status/896523232098078720
```bash 
python main.py -thread https://twitter.com/BarackObama/status/896523232098078720
```
or

```bash 
python main.py -thread 896523232098078720
```
  
## Contributing  
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.  
  
Please make sure to update tests as appropriate.  
  
## Thank you  
Thanks [Tweepy: Twitter for Python!](https://github.com/tweepy/tweepy) 🙂

## License  
  
[ GNU GPLv3 ](https://choosealicense.com/licenses/gpl-3.0/)  
  
