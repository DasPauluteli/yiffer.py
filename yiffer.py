import os
import cmd
import sys
import time
import json
import urllib.request
from urllib.parse import quote
import datetime

try:
	print('Starting up...')

	# Check Python version
	if sys.version_info[0] < 3:
		raise Exception("This program requires Python 3 or greater. Please update your installation.")

	def cls():
		os.system('cls' if os.name=='nt' else 'clear')

	def log(type, message):
		class c:
			HEADER = '\033[95m'
			OKBLUE = '\033[94m'
			OKGREEN = '\033[92m'
			WARNING = '\033[93m'
			FAIL = '\033[91m'
			ENDC = '\033[0m'
			BOLD = '\033[1m'
			UNDERLINE = '\033[4m'

		now = datetime.datetime.now()
		timestamp = f"["+now.strftime("%Y-%m-%d %H:%M")+"]"
		log = ""

		if type == "info":
			log = f"{c.OKBLUE}[INFO] {c.ENDC}{message}"
		elif type == "warn":
			log = f"{c.WARNING}[WARN] {c.ENDC}{message}"
		elif type == "err":
			log = f"{c.FAIL}[ERR] {c.ENDC}{message}"
		elif type == "success":
			log = f"{c.OKGREEN}[SUCCESS] {c.ENDC}{message}"
		else:
			log = f"[LOG] {message}"

		return print(f"{timestamp} {log}")

	DIR        = os.getcwd()
	OUTPUT_DIR = DIR + "/output"
	BASE_URL   = "http://yiffer.xyz"
	COMIC_URL  = BASE_URL + "/comics"
	API_URL    = BASE_URL + "/api/comics"
	SPLASH     = [
		"┌─────────────────────────────────────────────────────────────────────────┐",
		"│                                                                         │",
		"│                                                                         │",
		"│                      _   __   __                                        │",
		"│                     (_) / _| / _|                                       │",
		"│               _   _  _ | |_ | |_  ___  _ __  _ __   _   _               │",
		"│              | | | || ||  _||  _|/ _ \| '__|| '_ \ | | | |              │",
		"│              | |_| || || |  | | |  __/| | _ | |_) || |_| |              │",
		"│               \__, ||_||_|  |_|  \___||_|(_)| .__/  \__, |              │",
		"│                __/ |                        | |      __/ |              │",
		"│               |___/                         |_|     |___/               │",
		"│                                                                         │",
		"│                                                                         │",
		"├─────────────────────────────────────────────────────────────────────────┤",
		"│      « (c) 2014 - " + str(datetime.datetime.now().year) + " Caprine Softworks, powered by goat butts »       │",
		"└─────────────────────────────────────────────────────────────────────────┘"
	]
	USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36"

	if not os.path.exists(OUTPUT_DIR):
		os.makedirs(OUTPUT_DIR)
		log("success", "Created output directory!")
	else:
		log("success", "Output directory already exists!")

	cls()

	print("\033[95m" + "\n".join(SPLASH) + "\033[0m")

	class Yiffer(cmd.Cmd):
		intro = "Type \033[95m\"help\"\033[0m for a list of commands. Type \033[95m\"exit\"\033[0m to exit."
		prompt = "\033[95mY> \033[0m"

		def do_exit(self, arg):
			'Closes the application:  EXIT'
			print("\nStopping program...")
			return True

		"""
			Attempts to download comic images from the provided comic name
		"""
		def do_download(self, arg):
			'Downloads images from a yiffer.xyz comic URL:  download Closet Case 2'
			if (len(arg) < 1):
				return print("Missing argument")

			comic_name = str(" ".join(parse(arg)))
			encoded_comic_name = quote(comic_name)
			url = API_URL + "/" + encoded_comic_name

			log("info", "Checking for comic ["+comic_name+"]...")

			req = urllib.request.Request(
				url,
				data = None,
				headers = {
					'User-Agent': USER_AGENT
				}
			)
			
			f = urllib.request.urlopen(req)
			data = json.loads(f.read().decode('utf-8'))

			if "error" in data:
				return log("error", f"Error looking for comic: {data['error']}")
			else:
				download_dir = OUTPUT_DIR + "/" + comic_name
				page_count = data['numberOfPages']
				log("success", f"Comic exists! Preparing to download {page_count} pages...")

				start_time = time.time()

				if not os.path.exists(download_dir): os.makedirs(download_dir)

				for page in range(page_count):
					page_file = f"{(page+1):02}.jpg"
					page_url = f"{COMIC_URL}/{encoded_comic_name}/{page_file}"
					output_file = f"{OUTPUT_DIR}/{comic_name}/{page_file}"

					dl_req = urllib.request.Request(
						page_url,
						data = None,
						headers = {
							'User-Agent': USER_AGENT
						}
					)

					if os.path.exists(output_file):
						log("warn", f"Page {page_file} already exists, skipping...")
					else:
						log("info", f"Downloading page {page_file}...")
						# TODO: Potentially rewrite
						f = open(output_file, "wb")
						r = urllib.request.urlopen(dl_req)
						content = r.read()
						f.write(content)
						f.close()
						log("success", f"Downloaded page {page_file}")
						time.sleep(0.5)
				
				elapsed_time = time.time() - start_time
				log("success", f"Finished operation in ~" + time.strftime("%H hours, %M minutes, %S seconds", time.gmtime(elapsed_time)))

	def parse(arg):
		'Convert a series of zero or more numbers to an argument tuple'
		return tuple(map(str, arg.split()))

	if __name__ == '__main__':
		Yiffer().cmdloop()

except KeyboardInterrupt:
	print("\nStopping program...")