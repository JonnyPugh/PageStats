from requests import Session

# Get the information from specified posts using a worker thread/Queue design
# Provide an interface to get useful statistics about the posts

class Stats(object):
	def __init__(self, access_token, post_ids):
		self.__api_url = "https://graph.facebook.com/v2.10/"
		self.__session = Session()
		self.__session.params = {"access_token": access_token}
		self.__post_ids = post_ids

	def __request(self, path):
		r = self.__session.get(path)
		r.raise_for_status()
		return r.json()
