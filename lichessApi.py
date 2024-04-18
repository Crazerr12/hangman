import re
import time

import berserk
import pyaudio
import speech_recognition as sr
import whisper

token = "lip_5opuD6lGTSZCocZwJOw7"
recognizer = sr.Recognizer()
microphone = sr.Microphone()
session = berserk.TokenSession(token=token)
client = berserk.Client(session=session)


def record_and_recognize_audio():
    """
    Запись и разпознавание речи
    :return:
    """
    move = ""
    is_while = True
    with microphone:

        recognizer.adjust_for_ambient_noise(microphone, duration=2)

        chessboard_cells = (
            "a1", "b1", "c1", "d1", "e1", "f1", "g1", "h1",
            "a2", "b2", "c2", "d2", "e2", "f2", "g2", "h2",
            "a3", "b3", "c3", "d3", "e3", "f3", "g3", "h3",
            "a4", "b4", "c4", "d4", "e4", "f4", "g4", "h4",
            "a5", "b5", "c5", "d5", "e5", "f5", "g5", "h5",
            "a6", "b6", "c6", "d6", "e6", "f6", "g6", "h6",
            "a7", "b7", "c7", "d7", "e7", "f7", "g7", "h7",
            "a8", "b8", "c8", "d8", "e8", "f8", "g8", "h8"
        )

        while is_while:
            try:
                print("Listening...")
                audio = recognizer.listen(microphone, 5, 5)
                with open("output.wav", "wb") as file:
                    file.write(audio.get_wav_data())
            except sr.WaitTimeoutError:
                print("Can you check if your microphone is on, please?")
                return

            try:
                print("Started recognition...")
                model = whisper.load_model("base")
                result = model.transcribe("output.wav", fp16=False)
                move_text = result['text'].lower()
                print(move_text)
                move_list = re.split(r'[,.\s-]', move_text)
                print(move_list)
                if len(move_list) == 5:
                    move_list = (move_list[1]+move_list[2], move_list[3]+move_list[4])
                    move_text = move_list
                if len(move_list) == 4:
                    move_list = (move_list[0] + move_list[1], move_list[2] + move_list[3])
                    move_text = move_list
                for cell in chessboard_cells:
                    if cell in move_text:
                        move = "".join(move_list)
                        is_while = False
                        break
            except sr.UnknownValueError:
                pass

    return move


audio_devices = pyaudio.PyAudio()

for event in client.board.stream_incoming_events():
    if event['type'] == 'gameStart':
        game = event['game']
        game_id = game['id']
        isMyTurn = game["isMyTurn"]
        while True:
            if isMyTurn:
                move = record_and_recognize_audio()
                print(move)
                try:
                    client.board.make_move(game_id=game_id, move=move)
                except:
                    continue
                isMyTurn = False
            else:
                time.sleep(1)
                isMyTurn = True
