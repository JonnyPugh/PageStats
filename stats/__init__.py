from Queue import Queue
from requests import Session
import threading

class Stats(object):
	def __request(self, path):
		r = self.__session.get(path)
		r.raise_for_status()
		return r.json()

	def __get_post_data(self):
			while not self.__ids_to_process.empty():
				reactions = self.__request(self.__api_url + self.__ids_to_process.get() + "/reactions")
				while reactions["data"]:
					for reaction in reactions["data"]:
						user_id = reaction["id"]
						reaction_type = reaction["type"]

						self.__lock.acquire()
						self.__user_names[user_id] = reaction["name"]
						if user_id not in self.__users:
							self.__users[user_id] = {}
						if reaction_type not in self.__users[user_id]:
							self.__users[user_id][reaction_type] = 0
						self.__users[user_id][reaction_type] += 1
						self.__lock.release()
					if "next" not in reactions["paging"]:
						break
					reactions = self.__(reactions["paging"]["next"])
				self.__ids_to_process.task_done()

	def __init__(self, access_token, post_ids, num_threads=64):
		self.__users = {}
		self.__user_names = {}
		self.__num_posts = len(post_ids)
		self.__api_url = "https://graph.facebook.com/v2.10/"
		self.__session = Session()
		self.__session.params = {"access_token": access_token}
		self.__lock = threading.Lock()
		self.__ids_to_process = Queue()
		for post_id in post_ids:
			self.__ids_to_process.put(post_id)

		for _ in range(num_threads):
			thread = threading.Thread(target=self.__get_post_data)
			thread.daemon = True
			thread.start()

	# Interface (use self.__ids_to_process.join() for every function in the interface):
	# Top Post
	# List of posts in order of popularity
	# Function to get a string representing top n posts
	# Top Reactor
	# List of reactors in order of how many reactions
	# Function to get a string representing top n reactors

	def get_reactors_message(self, number_of_reactors=10):
		emoticons = {
		    "LIKE": "\xF0\x9F\x91\x8D",
		    "LOVE": "\xF0\x9F\x92\x9F",
		    "HAHA": "\xF0\x9F\x98\x86",
		    "WOW": "\xF0\x9F\x98\xAE",
		    "SAD": "\xF0\x9F\x98\xA2",
		    "ANGRY": "\xF0\x9F\x98\xA1",
		    "THANKFUL": "\xF0\x9F\x8C\xB8",
		    "PRIDE": "\xF0\x9F\x8C\x88"
			}
		overall_total_reactions = 0
		users_info = []
		message = "***Top "+str(number_of_reactors)+" Reactors***\n"
		ranking = 1
		self.__ids_to_process.join()
		for user_id, user_info in self.__users.items():
			reactions_breakdown = " ".join([" ".join([emoticons[reaction_type], str(num)]) for (reaction_type, num) in sorted(user_info.items(), key=lambda x: x[1], reverse=True)])
			total_reactions = sum(user_info.values())
			users_info.append((total_reactions, self.__user_names[user_id]+" - "+str(total_reactions)+": "+reactions_breakdown.decode("utf-8")))
			overall_total_reactions += total_reactions
		for reactions_info in sorted(users_info, key=lambda x: x[0], reverse=True)[:number_of_reactors]:
			message += str(ranking)+". "+reactions_info[1]+"\n"
			ranking += 1
		return message + "Average reactions per post: "+str(float(overall_total_reactions) / self.__num_posts)
