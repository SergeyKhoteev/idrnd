import json
import telebot
from pydub import AudioSegment
import face_recognition


def main():
	database = get_records_db()
	bot = telebot.TeleBot("5781085041:AAGe-OnSffBLE8jSQ1AaAbvX_1rK5osoVTc")
	
	@bot.message_handler(content_types=['text', 'voice', 'photo'])
	def get_messages(message):
		if message.content_type == 'voice':
			file_name = get_file_name(user_id = str(message.from_user.id), database = database, section = 'audio')
			voice_processing(bot = bot, message = message, file_name = file_name)
			with open('database.json', 'w') as file:
				json.dump(database, file)
			bot.send_message(message.from_user.id, f'voice uploaded {file_name}')
		if message.content_type == 'photo':
			photo_processing(bot = bot, message = message, database = database)

	bot.polling(none_stop=True, interval=0)


### Downloads audiofile and converts it to ".wav" with 16KHz frame_rate
def voice_processing(bot, message, file_name):

	### Uploads telegram file
	file_info = bot.get_file(message.voice.file_id)
	downloaded_file = bot.download_file(file_info.file_path)
	with open(f'{file_name}', 'wb') as new_file:
		new_file.write(downloaded_file)

	### Converts it to wav with preselected frame rate
	audio = AudioSegment.from_file(f"{file_name}")
	audio = audio.set_frame_rate(16000)
	audio.export(f"{file_name}", format="wav", bitrate = '128k')


### Downloads photo and tries to find face
def photo_processing(bot, message, database):
	file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)
	downloaded_file = bot.download_file(file_info.file_path)
	with open('support/temp', 'wb') as file:
		file.write(downloaded_file)
	image = face_recognition.load_image_file("support/temp")
	face_locations = face_recognition.face_locations(image)
	if face_locations != []:
		file_name = get_file_name(user_id = str(message.from_user.id), database = database, section = 'photo')
		with open(file_name, 'wb') as file:
			file.write(downloaded_file)
		with open('database.json', 'w') as file:
			json.dump(database, file)
		bot.send_message(message.from_user.id, f'face detected, photo uploaded {file_name}')
	else:
		bot.send_message(message.from_user.id, f'no faces :(')


### Checks is database already exists. Return database as a dict.
def get_records_db():
	try:
		with open('database.json', 'r') as file:
			database = json.load(file)
	except FileNotFoundError:
		database = {'audio': {}, 'photo': {}}
	return database


### Creates database record and returns filename for audio file.
def get_file_name(user_id, database, section):
	if user_id in database[section].keys():
		database[section][user_id].append(database[section][user_id][-1] + 1)
		index = str(database[section][user_id][-1])
		file_name = user_id + f' --> {section}_message_' + index
	else:
		database[section][user_id] = [0]
		file_name = user_id + f' --> {section}_message_0'
	return file_name


if __name__ == '__main__':
	main()
