from requests import Session

# Get all posts on a page
# Get the information from those posts using a worker thread/Queue design
# Provide an interface to get useful statistics about the posts

class Stats(object):
	def __init__(self, access_token):
		self.__api_url = "https://graph.facebook.com/v2.10/"
		self.__session = Session()
		self.__session.params = {"access_token": access_token}

		posts = self.__request(self.__api_url + "me/posts")
		self.__posts = posts["data"]
		while "next" in posts["paging"]:
			posts = self.__request(posts["paging"]["next"])
			self.__posts.extend(posts["data"])

	def __request(self, path):
		r = self.__session.get(path)
		r.raise_for_status()
		return r.json()
