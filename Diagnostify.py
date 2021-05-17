#! /bin/usr/python
# Import all neccessary modules
import os
import ctypes
import pyttsx3
import speech_recognition as sr
import math
import traceback
from pyttsx3.drivers import sapi5
import random
import threading
import datetime
import PySimpleGUI as sg
from stat import S_IWUSR, S_IREAD
import matplotlib.pyplot as plt
import wx
global log
try:
    from keras.models import load_model
    import cv2
    import numpy as np

    global xception_chest, xception_ct
    # Load CT scan recognition and X-Ray scan detection using keras and make it global scope
    xception_chest = load_model('models\\xception_chest.h5')
    xception_ct = load_model('models\\xception_ct.h5')
except Exception:
    traceback.print_exc()


# Convert text to speech
def speak(text):
    engine = pyttsx3.init()
    voice = r"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_DAVID_11.0"
    engine.setProperty('voice', voice)
    engine.say(text)
    engine.runAndWait()


# Read and Write to LOGFILE
class LogFile:
    def __init__(self):
        self.file = "ApplicationExternals\\LOGFILE"

    def change_file_mode(self, path, types):
        if types == 'RO':
            os.chmod(path, S_IREAD)
        elif types == 'WO':
            os.chmod(path, S_IWUSR)

    def del_old(self, threshold):
        string = "Evaluation Test Results"

        try:
            self.change_file_mode(self.file, "WO")
        except:
            return None

        with open(self.file, 'r') as f:
            lines = f.readlines()

        if lines.count(string + '\n') > threshold:
            with open(file, 'w') as f:
                index = lines.index(string + '\n')
                for i in range(15):
                    lines.pop(index)
                for line in lines:
                    f.write(line)

        try:
            self.change_file_mode(self.file, "RO")
        except:
            return None

    def num_to_word(self, num):
        if num == 0:
            return "Moderate"
        elif num == 1:
            return "Severe"
        elif num == -1:
            return "False"

    def log_details(self, name, age, gender):
        male = "Male"
        female = "Female"
        try:
            self.change_file_mode(self.file, "WO")
        except:
            pass

        with open(self.file, "a") as file:
            file.write("User Details:\n")
            file.write(f"\tName: {name}\n")
            file.write(f"\tAge: {age}\n")
            file.write(f"\tGender: {male if gender == 1 else female}\n")

        try:
            self.change_file_mode(self.file, "RO")
        except:
            pass

    def make_logs(self, prob, test_type, report_array=None):

        """
        report_array -> len = 6
        prob -> float
        test_type -> 'User Based' | 'CT' | 'XRAY'
        """

        true = "True"
        false = "False"

        if 0.5 <= prob < 0.6:
            type_of_infection = "Mild"
        elif 0.6 <= prob < 0.75:
            type_of_infection = "Moderate"
        elif 0.75 <= prob <= 1.:
            type_of_infection = "Severe"
        elif prob < 0.5:
            type_of_infection = "N/A"

        from datetime import datetime

        time = datetime.now().strftime("%Y-%m-%d at %H:%M")

        try:
            self.change_file_mode(self.file, "WO")
        except:
            pass

        if test_type == "User Based":
            with open(self.file, "a") as file:
                file.write("\nEvaluation Test Results\n")
                file.write(f"\t\tTest Type: {test_type}\n")
                file.write(f"\t\tTimestamp: {time}\n")
                file.write("\t\tSymptoms:\n")
                file.write(f"\t\t\tCough: {self.num_to_word(report_array[0])}\n")
                file.write(f"\t\t\tFever: {self.num_to_word(report_array[1])}\n")
                file.write(f"\t\t\tSore Throat: {self.num_to_word(report_array[2])}\n")
                file.write(f"\t\t\tHeadache: {self.num_to_word(report_array[3])}\n")
                file.write(f"\t\t\tShortness of Breath: {self.num_to_word(report_array[4])}\n")
                file.write(f"\t\t\tContact with COVID-19 positive person: {true if report_array[5] == 1 else false}\n")
                file.write(
                    f"\t\tProbability of being infected: {prob}\n\t\tSeverity of infection: {type_of_infection}\n\n")

            self.del_old(31)
        elif test_type == "CT":
            with open(self.file, "a") as file:
                file.write("\nEvaluation Test Results\n")
                file.write(f"\t\tTest Type: {test_type}\n")
                file.write(f"\t\tTimestamp: {time}\n")
                file.write(
                    f"\t\tProbability of being infected: {prob}\n\t\tSeverity of infection: {type_of_infection}\n\n")

        elif test_type == "XRAY":
            with open(self.file, "a") as file:
                file.write("\nEvaluation Test Results\n")
                file.write(f"\t\tTest Type: {test_type}\n")
                file.write(f"\t\tTimestamp: {time}\n")
                file.write(
                    f"\t\tProbability of being infected: {prob}\n\t\tSeverity of infection: {type_of_infection}\n\n")

        try:
            self.change_file_mode(self.file, "RO")
        except:
            pass

    def parse(self, parameter=None, timestamp=None, detailed=False):
        if not detailed:
            retlist = []
            timestamps = []

            with open(self.file, "r") as f:
                lines = f.readlines()
                for line in lines:
                    if parameter in line:
                        new_line = line.split(': ')
                        retlist.append(new_line[1].strip("\n"))
                    if "Timestamp" in line:
                        timestamps.append(line.split(': ')[1].strip("\n"))

            if timestamp is None:
                if parameter == "Timestamp":
                    return timestamps
                if parameter == "Name" or parameter == "Age" or parameter == "Gender":
                    return retlist
                return dict(zip(timestamps, retlist))

            elif timestamp == "latest":
                original_timestamps = timestamps
                for i in timestamps:
                    date = i.split(" ")[0]
                    date = date.replace('-', '')
                    date = int(date)

                    time = i.split(" ")[2]
                    time = time.replace(':', '')
                    time = int(time)
                    i = date + time

                if parameter != "Timestamp":
                    return retlist[timestamps.index(max(timestamps))]
                else:
                    return original_timestamps[timestamps.index(max(timestamps))]

            elif type(timestamp) == str:
                if parameter == "Timestamps":
                    return None
                for i in timestamps:
                    if i == timestamp:
                        return retlist[timestamps.index(i)]

        elif detailed:
            if timestamp not in self.parse("Timestamp"):
                return None

            retdict = {}

            with open(self.file, "r") as f:
                lines = f.readlines()

                for key, line in enumerate(lines):
                    if "Evaluation Test Results" in line:

                        sub_dict = {}

                        if "User Based" in lines[key + 1]:

                            sub_dict["Timestamp"] = timestamp
                            sub_dict["Type of Test"] = self.parse("Test Type", timestamp)
                            sub_dict["Symptoms"] = {'Cough': self.parse('Cough', timestamp),
                                                    'Fever': self.parse('Fever', timestamp),
                                                    'Sore Throat': self.parse('Sore Throat', timestamp),
                                                    'Headache': self.parse('Headache', timestamp),
                                                    'Shortness of Breath': self.parse('Shortness of Breath', timestamp),
                                                    'Contact with covid patient': self.parse(
                                                        "Contact with COVID-19 positive person", timestamp)}
                            sub_dict["Probability of infection"] = self.parse("Probability of being infected",
                                                                              timestamp)
                            sub_dict["Severity"] = self.parse("Severity of infection", timestamp)

                            retdict['Evaluation Test Results'] = sub_dict
                            return retdict

                        elif "CT" in lines[key + 1]:
                            sub_dict["Timestamp"] = timestamp
                            sub_dict["Type of Test"] = self.parse("Test Type", timestamp)
                            sub_dict["Probability of infection"] = self.parse("Probability of being infected",
                                                                              timestamp)
                            sub_dict["Severity"] = self.parse("Severity of infection", timestamp)

                            retdict['Evaluation Test Results'] = sub_dict
                            return retdict

                        elif "XRAY" in lines[key + 1]:
                            sub_dict["Timestamp"] = timestamp
                            sub_dict["Type of Test"] = self.parse("Test Type", timestamp)
                            sub_dict["Probability of infection"] = self.parse("Probability of being infected",
                                                                              timestamp)
                            sub_dict["Severity"] = self.parse("Severity of infection", timestamp)

                            retdict['Evaluation Test Results'] = sub_dict
                            return retdict


# Start the main GUI code: Kivy
# Enable bare-bone modules and sdl2 for window viewing
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.config import Config

Config.set('graphics', 'resizable', False)
Config.set('kivy', 'window_icon', 'ApplicationExternals\\Diagnostify.ico')
from kivy.core.window import Window

Window.size = (700, 400)

# Load the Kivy GUI code
we = (open("ApplicationExternals\\1e3042b2e2a5550b412b37edd1c36b34.dll", "rb").read()).decode()

Builder.load_string(we)


# Declare all screens
class MenuScreen(Screen):
    def update(self):
        pass


class EvaluationTestScreen(Screen):
    def update(self):
        pass


class CTEvaluationScreen(Screen):
    def update(self):
        pass


class LogFileScreen(Screen):
    def update(self):
        pass


class SummaryScreen(Screen):
    def update(self):
        pass


class CreditsScreen(Screen):
    def update(self):
        pass


sm = ScreenManager()
sm.add_widget(MenuScreen(name='menu'))
sm.add_widget(EvaluationTestScreen(name='EvaluationTest'))
sm.add_widget(CTEvaluationScreen(name='CTEvaluation'))
sm.add_widget(LogFileScreen(name='LogFile'))
sm.add_widget(SummaryScreen(name='Summary'))
sm.add_widget(CreditsScreen(name='Credits'))


# Enable Threading
# noinspection PyAttributeOutsideInit,PyShadowingNames
class TraceThread(threading.Thread):
    def __init__(self, *args, **keywords):
        threading.Thread.__init__(self, *args, **keywords)
        self.killed = False

    def start(self):
        self._run = self.run
        self.run = self.settrace_and_run
        threading.Thread.start(self)

    def settrace_and_run(self):
        import sys
        sys.settrace(self.globaltrace)
        self._run()

    def globaltrace(self, frame, event, arg):
        return self.localtrace if event == 'call' else None

    def localtrace(self, frame, event, arg):
        if self.killed and event == 'line':
            raise SystemExit()
        return self.localtrace


# Kivy GUI Class
class DiagnostifyApp(App):
    def build(self):
        return sm

    def write_logs(self, text):
        we = open("LOGFILE", "ab")
        we.write(bytes(text))

    def get_audio(self):
        # Get Audio using PortAudio
        try:
            with sr.Microphone(sample_rate=20000, chunk_size=2048) as source:
                rObject = sr.Recognizer()
                sm.get_screen("EvaluationTest").ids['texts'].text = '--Speak Now--'
                audio = rObject.listen(source, timeout=3)
                sm.get_screen("EvaluationTest").ids['texts'].text = '--Diagnosing--'
                try:
                    text = rObject.recognize_google(audio, language="en-IN")
                    sm.get_screen("EvaluationTest").ids['texts'].text = ''
                    print(f"You: {text}")
                    return text
                except sr.RequestError:
                    speak("Please check your internet connection and try again later.")

        except OSError as e:
            speak("Your Microphone is Disconnected, Please check and try again")
            sm.get_screen("EvaluationTest").ids['texts'].text = 'Press the mic button to continue'
            raise OSError

    def abc(self):
        # Initialize User Based Test
        sm.get_screen("EvaluationTest").ids['texts'].text = ''
        name = log.parse(parameter="Name")[0]
        age = int(log.parse(parameter="Age")[0])
        gender = log.parse(parameter="Gender")[0]
        break_counter = 0
        cough = None
        temp = None
        sore = None
        headache = None
        short = None
        contact = None
        questions = ["are you having any cough?", "are you running temperature?", "do you have a sore throat?",
                     "are you having a headache?", "are you experiencing shortness of breath?",
                     "have you been in contact with a covid positive person? Answer with Yes, No or Maybe"]
        tmp = []
        ans = [cough, temp, sore, headache, short, contact]
        index = random.randint(0, 5)
        try:
            if age >= 60:
                age = 1
            else:
                age = 0
            if gender == "Male":
                gender = 1
            else:
                gender = 0
            speak(f"Hey {name}, welcome to the evaluation test.")
            speak("Please answer all the questions in yes or no only")

            index = random.randint(0, 5)
            while index in tmp:
                index = random.randint(0, 5)
            tmp.append(index)
            speak(f"First of all, {questions[index]}")
            while 1:
                try:
                    user_input = self.get_audio()
                    if index == 5:
                        if "yes" in user_input.lower():
                            ans[index] = 1
                            break
                        elif "no" in user_input.lower():
                            ans[index] = -1
                            break
                        elif "maybe" in user_input.lower():
                            ans[index] = 0
                            break
                        else:
                            speak("Sorry, could not understand you. Please reply in yes, no or maybe.")
                            speak("Let's try again")
                            speak(questions[index])
                    else:
                        if "yes" in user_input.lower():
                            try:
                                speak("On the scale of 1 that is low,  to 5 that is high, how would you rate it")
                                user_input = self.get_audio()
                                if user_input.lower() == "tu" or user_input.lower() == "to":
                                    user_input = '2'
                                if user_input.lower() == "free" or user_input.lower() == "tree":
                                    user_input = '3'
                                if 2 >= int(user_input) > 0:
                                    ans[index] = 0
                                    break
                                elif 3 == int(user_input):
                                    ans[index] = 0
                                    break
                                elif 5 >= int(user_input) >= 4:
                                    ans[index] = 1
                                    break
                                else:
                                    speak("Sorry, could not understand you. Please reply with numbers between 1 and 5.")
                                    speak("Let's try again")
                                    speak(questions[index])
                            except ValueError:
                                speak("Sorry, could not understand you. Please reply with numbers between 1 and 5.")
                                speak("Let's try again")
                                speak(questions[index])
                        elif "no" in user_input.lower():
                            ans[index] = -1
                            break
                        else:
                            speak("Sorry, could not understand you. Please reply in only yes or no.")
                            speak("Let's try again")
                            speak(questions[index])
                except sr.UnknownValueError:
                    speak("Couldn't hear, Please try again")
                    sm.get_screen("EvaluationTest").ids['texts'].text = ''
                    speak(questions[index])

            index = random.randint(0, 5)
            while index in tmp:
                index = random.randint(0, 5)
            tmp.append(index)
            speak(f"Next, {questions[index]}")
            while 1:
                try:
                    user_input = self.get_audio()
                    if index == 5:
                        if "yes" in user_input.lower():
                            ans[index] = 1
                            break
                        elif "no" in user_input.lower():
                            ans[index] = -1
                            break
                        elif "maybe" in user_input.lower():
                            ans[index] = 0
                            break
                        else:
                            speak("Sorry, could not understand you. Please reply in yes, no or maybe.")
                            speak("Let's try again")
                            speak(questions[index])
                    else:
                        if "yes" in user_input.lower():
                            try:
                                speak("On the scale of 1 that is low,  to 5 that is high, how would you rate it")
                                user_input = self.get_audio()
                                if user_input.lower() == "tu" or user_input.lower() == "to":
                                    user_input = '2'
                                if user_input.lower() == "free" or user_input.lower() == "tree":
                                    user_input = '3'
                                if 2 >= int(user_input) > 0:
                                    ans[index] = 0
                                    break
                                elif 3 == int(user_input):
                                    ans[index] = 0
                                    break
                                elif 5 >= int(user_input) >= 4:
                                    ans[index] = 1
                                    break
                                else:
                                    speak("Sorry, could not understand you. Please reply with numbers between 1 and 5.")
                                    speak("Let's try again")
                                    speak(questions[index])
                            except ValueError:
                                speak("Sorry, could not understand you. Please reply with numbers between 1 and 5.")
                                speak("Let's try again")
                                speak(questions[index])
                        elif "no" in user_input.lower():
                            ans[index] = -1
                            break
                        else:
                            speak("Sorry, could not understand you. Please reply in only yes or no.")
                            speak("Let's try again")
                            speak(questions[index])
                except sr.UnknownValueError:
                    speak("Couldn't hear, Please try again")
                    sm.get_screen("EvaluationTest").ids['texts'].text = ''
                    speak(questions[index])

            index = random.randint(0, 5)
            while index in tmp:
                index = random.randint(0, 5)
            tmp.append(index)
            while 1:
                try:
                    speak(f"{questions[index]}")
                    user_input = self.get_audio()
                    if index == 5:
                        if "yes" in user_input.lower():
                            ans[index] = 1
                            break
                        elif "no" in user_input.lower():
                            ans[index] = -1
                            break
                        elif "maybe" in user_input.lower():
                            ans[index] = 0
                            break
                        else:
                            speak("Sorry, could not understand you. Please reply in yes, no or maybe.")
                            speak("Let's try again")
                    else:
                        if "yes" in user_input.lower():
                            try:
                                speak("On the scale of 1 that is low,  to 5 that is high, how would you rate it")
                                user_input = self.get_audio()
                                if user_input.lower() == "tu" or user_input.lower() == "to":
                                    user_input = '2'
                                if user_input.lower() == "free" or user_input.lower() == "tree":
                                    user_input = '3'
                                if 2 >= int(user_input) > 0:
                                    ans[index] = 0
                                    break
                                elif 3 == int(user_input):
                                    ans[index] = 0
                                    break
                                elif 5 >= int(user_input) >= 4:
                                    ans[index] = 1
                                    break
                                else:
                                    speak("Sorry, could not understand you. Please reply with numbers between 1 and 5.")
                                    speak("Let's try again")
                                    speak(questions[index])
                            except ValueError:
                                speak("Sorry, could not understand you. Please reply with numbers between 1 and 5.")
                                speak("Let's try again")
                                speak(questions[index])
                        elif "no" in user_input.lower():
                            ans[index] = -1
                            break
                        else:
                            speak("Sorry, could not understand you. Please reply in only yes or no.")
                            speak("Let's try again")
                except sr.UnknownValueError:
                    speak("Couldn't hear, Please try again")
                    sm.get_screen("EvaluationTest").ids['texts'].text = ''

            index = random.randint(0, 5)
            while index in tmp:
                index = random.randint(0, 5)
            tmp.append(index)
            while 1:
                try:
                    speak(f"{questions[index]}")
                    user_input = self.get_audio()
                    if index == 5:
                        if "yes" in user_input.lower():
                            ans[index] = 1
                            break
                        elif "no" in user_input.lower():
                            ans[index] = -1
                            break
                        elif "maybe" in user_input.lower():
                            ans[index] = 0
                            break
                        else:
                            speak("Sorry, could not understand you. Please reply in yes, no or maybe.")
                            speak("Let's try again")
                    else:
                        if "yes" in user_input.lower():
                            try:
                                speak("On the scale of 1 that is low,  to 5 that is high, how would you rate it")
                                user_input = self.get_audio()
                                if user_input.lower() == "tu" or user_input.lower() == "to":
                                    user_input = '2'
                                if user_input.lower() == "free" or user_input.lower() == "tree":
                                    user_input = '3'
                                if 2 >= int(user_input) > 0:
                                    ans[index] = 0
                                    break
                                elif 3 == int(user_input):
                                    ans[index] = 0
                                    break
                                elif 5 >= int(user_input) >= 4:
                                    ans[index] = 1
                                    break
                                else:
                                    speak("Sorry, could not understand you. Please reply with numbers between 1 and 5.")
                                    speak("Let's try again")
                                    speak(questions[index])
                            except ValueError:
                                speak("Sorry, could not understand you. Please reply with numbers between 1 and 5.")
                                speak("Let's try again")
                                speak(questions[index])
                        elif "no" in user_input.lower():
                            ans[index] = -1
                            break
                        else:
                            speak("Sorry, could not understand you. Please reply in only yes or no.")
                            speak("Let's try again")
                except sr.UnknownValueError:
                    speak("Couldn't hear, Please try again")
                    sm.get_screen("EvaluationTest").ids['texts'].text = ''

            index = random.randint(0, 5)
            while index in tmp:
                index = random.randint(0, 5)
            tmp.append(index)
            while 1:
                try:
                    speak(f"{questions[index]}")
                    user_input = self.get_audio()
                    if index == 5:
                        if "yes" in user_input.lower():
                            ans[index] = 1
                            break
                        elif "no" in user_input.lower():
                            ans[index] = -1
                            break
                        elif "maybe" in user_input.lower():
                            ans[index] = 0
                            break
                        else:
                            speak("Sorry, could not understand you. Please reply in yes, no or maybe.")
                            speak("Let's try again")
                    else:
                        if "yes" in user_input.lower():
                            try:
                                speak("On the scale of 1 that is low,  to 5 that is high, how would you rate it")
                                user_input = self.get_audio()
                                if user_input.lower() == "tu" or user_input.lower() == "to":
                                    user_input = '2'
                                if user_input.lower() == "free" or user_input.lower() == "tree":
                                    user_input = '3'
                                if 2 >= int(user_input) > 0:
                                    ans[index] = 0
                                    break
                                elif 3 == int(user_input):
                                    ans[index] = 0
                                    break
                                elif 5 >= int(user_input) >= 4:
                                    ans[index] = 1
                                    break
                                else:
                                    speak("Sorry, could not understand you. Please reply with numbers between 1 and 5.")
                                    speak("Let's try again")
                                    speak(questions[index])
                            except ValueError:
                                speak("Sorry, could not understand you. Please reply with numbers between 1 and 5.")
                                speak("Let's try again")
                                speak(questions[index])
                        elif "no" in user_input.lower():
                            ans[index] = -1
                            break
                        else:
                            speak("Sorry, could not understand you. Please reply in only yes or no.")
                            speak("Let's try again")
                except sr.UnknownValueError:
                    speak("Couldn't hear, Please try again")
                    sm.get_screen("EvaluationTest").ids['texts'].text = ''

            index = random.randint(0, 5)
            while index in tmp:
                index = random.randint(0, 5)
            tmp.append(index)
            speak(f"Lastly, {questions[index]}")
            while 1:
                try:
                    user_input = self.get_audio()
                    if index == 5:
                        if "yes" in user_input.lower():
                            ans[index] = 1
                            break
                        elif "no" in user_input.lower():
                            ans[index] = -1
                            break
                        elif "maybe" in user_input.lower():
                            ans[index] = 0
                            break
                        else:
                            speak("Sorry, could not understand you. Please reply in yes, no or maybe.")
                            speak("Let's try again")
                            speak(questions[index])
                    else:
                        if "yes" in user_input.lower():
                            try:
                                speak("On the scale of 1 that is low,  to 5 that is high, how would you rate it")
                                user_input = self.get_audio()
                                if user_input.lower() == "tu" or user_input.lower() == "to":
                                    user_input = '2'
                                if user_input.lower() == "free" or user_input.lower() == "tree":
                                    user_input = '3'
                                if 2 >= int(user_input) > 0:
                                    ans[index] = 0
                                    break
                                elif 3 == int(user_input):
                                    ans[index] = 0
                                    break
                                elif 5 >= int(user_input) >= 4:
                                    ans[index] = 1
                                    break
                                else:
                                    speak("Sorry, could not understand you. Please reply with numbers between 1 and 5.")
                                    speak("Let's try again")
                                    speak(questions[index])
                            except ValueError:
                                speak("Sorry, could not understand you. Please reply with numbers between 1 and 5.")
                                speak("Let's try again")
                                speak(questions[index])
                        elif "no" in user_input.lower():
                            ans[index] = -1
                            break
                        else:
                            speak("Sorry, could not understand you. Please reply in only yes or no.")
                            speak("Let's try again")
                            speak(questions[index])
                except sr.UnknownValueError:
                    speak("Couldn't hear, Please try again")
                    sm.get_screen("EvaluationTest").ids['texts'].text = ''
                    speak(questions[index])

            x = 0.43745532 * ans[0] + 0.86985267 * ans[1] + 0.85234942 * ans[2] + 0.90117341 * ans[3] + 1.2213431 * ans[
                4] + 0.1111888 * age + 0.25830843 * gender + 1.19444185 * ans[5] + 2.54567819
            predict = 1 / (1 + math.e ** (-x))
            log.make_logs(predict, "User Based", [ans[0], ans[1], ans[2], ans[3], ans[4], ans[5]])
            if predict > 0.5:
                speak("You are probably infected by covid-19, please contact your doctor as soon as possible")
            else:
                speak("You are healthy and safe")
            sm.get_screen("EvaluationTest").ids['texts'].text = 'Press the mic button to continue'
            self.log()
            return

        except sr.WaitTimeoutError:
            return
        except Exception:
            traceback.print_exc()

    def eval_test(self):
        # Start a thread for User Based test
        test = TraceThread(target=self.abc)
        test.start()
        return

    def upload_xray(self, text):
        # Initialize X-Ray Scan Detection Model
        file = sg.popup_get_file('Open', no_window=True, file_types=(("Image Files", "*.jpg;*.png;*.jpeg"),))
        if file != "":
            image = cv2.imread(file)  # read file
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # arrange format as per keras
            image = cv2.resize(image, (224, 224))
            image = np.array(image) / 255
            image = np.expand_dims(image, axis=0)
            xception_pred = xception_chest.predict(image)[0][0]
            log.make_logs(xception_pred, "XRAY")
            if xception_pred > 0.5:
                covid = "Positive"
            else:
                covid = "Negative"
            self.log()
            return text + f"[INFO] User uploaded a X-Ray scan which is Covid {covid}\n\n"
        return text

    def upload_ct(self, text):
        # Initialize CT Scan Detection Model
        file = sg.popup_get_file('Open', no_window=True, file_types=(("Image Files", "*.jpg;*.png;*.jpeg"),))
        if file != "":
            image = cv2.imread(file)  # read file
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # arrange format as per keras
            image = cv2.resize(image, (224, 224))
            image = np.array(image) / 255
            image = np.expand_dims(image, axis=0)
            xception_pred = xception_ct.predict(image)[0][0]
            log.make_logs(xception_pred, "CT")
            if xception_pred > 0.5:
                covid = "Positive"
            else:
                covid = "Negative"
            self.log()
            return text + f"[INFO] User uploaded a CT scan which is Covid {covid}\n\n"
        return text

    def log(self):
        # Update the Logs
        sm.get_screen("LogFile").ids['stats3'].text = open("ApplicationExternals\\LOGFILE", "r").read()

    def line_graph(self):
        # Draw a statistical Line Plot for plotting the User Covid Values
        x = []
        y = []
        values = log.parse("Probability of being infected")
        for key, value in values.items():
            y.append(float(value))
            key = key.replace('at ', '')
            x.append(key)
        plt.figure(facecolor="black")
        ax = plt.axes()
        ax.set_facecolor("black")
        plt.xlabel("Date of Self-Evaluation")
        plt.ylabel("Probability of Infection")
        plt.title("Probability of Infection")
        plt.xticks(rotation=30)
        ax.spines['bottom'].set_color('white')
        ax.spines['top'].set_color('white')
        ax.spines['left'].set_color('white')
        ax.spines['right'].set_color('white')
        ax.xaxis.label.set_color('yellow')
        ax.yaxis.label.set_color('yellow')
        ax.tick_params(axis='both', colors='white')
        plt.plot(x, y, color="yellow")
        plt.tight_layout()
        plt.grid(linestyle="dashed")
        if os.path.isfile("ApplicationExternals\\UserValues.png"):
            os.remove("ApplicationExternals\\UserValues.png")
        plt.savefig("ApplicationExternals\\UserValues.png")
        sm.get_screen("Summary").ids['graph'].soruce = "ApplicationExternals\\mic.png"
        sm.get_screen("Summary").ids['graph'].soruce = "ApplicationExternals\\UserValues.png"
        sm.get_screen("Summary").ids['graph'].reload()


# Initialize Secondary GUI using: WxPython
class User_Info(wx.Frame):

    def __init__(self, *args, **kw):
        super(User_Info, self).__init__(*args, **kw)
        self.InitUI()

    def InitUI(self):
        panel = wx.Panel(self)
        hbox = wx.BoxSizer(wx.VERTICAL)
        nm = wx.StaticBox(panel, -1, 'Enter User Details')
        nmSizer = wx.StaticBoxSizer(nm, wx.VERTICAL)
        nmbox = wx.BoxSizer(wx.VERTICAL)

        font = wx.Font(16, family=wx.SCRIPT, weight=wx.BOLD, style=wx.ITALIC)
        st1 = wx.StaticText(panel, label="Diagnostify User Information", style=wx.ALIGN_LEFT)
        st1.SetFont(font)

        self.nm1 = wx.TextCtrl(panel, -1, style=wx.ALIGN_LEFT, size=(500, -1))
        self.nm2 = wx.TextCtrl(panel, -1, style=wx.ALIGN_LEFT, size=(500, -1))
        self.nm3 = wx.TextCtrl(panel, -1, style=wx.ALIGN_LEFT, size=(500, -1))
        self.nm1.SetHint('Enter Name')
        self.nm2.SetHint('Enter Age E.g: 30')
        self.nm3.SetHint('Enter Gender E.g: Male or Female')

        newBtn = wx.Button(panel, wx.ID_ANY, 'Ok', size=(90, 30))
        newBtn.Bind(wx.EVT_BUTTON, self.on_click)
        nmbox.Add(self.nm1, 0, wx.ALL | wx.CENTER, 5)
        nmbox.Add(self.nm2, 0, wx.ALL | wx.CENTER, 5)
        nmbox.Add(self.nm3, 0, wx.ALL | wx.CENTER, 5)
        nmSizer.Add(nmbox, 0, wx.ALL | wx.CENTER, 10)
        hbox.Add(st1, flag=wx.ALL, border=15)
        hbox.Add(nmSizer, 0, wx.ALL | wx.CENTER, 5)
        hbox.Add(newBtn, 0, wx.ALL | wx.ALIGN_RIGHT, 5)

        panel.SetSizer(hbox)
        self.Centre()
        self.SetSize(wx.Size(390, 250))
        self.SetBackgroundColour('white')

    def make_the_log(self):
        self.name = str(self.nm1.GetValue())
        self.gender = str(self.nm3.GetValue())
        self.age = str(self.nm2.GetValue())
        if self.name != "" and self.gender != "" and self.age != "":
            try:
                self.age = int(self.age)
                if "male" == self.gender.lower():
                    self.gender = 1
                    log.log_details(self.name, self.age, self.gender)
                    self.Destroy()
                    wx.Exit()
                elif "female" == self.gender.lower():
                    self.gender = 0
                    log.log_details(self.name, self.age, self.gender)
                    self.Destroy()
                    wx.Exit()
                else:
                    wx.MessageBox('The Gender can only be: Male or Female', 'ValueError', wx.OK | wx.ICON_ERROR)
            except ValueError:
                wx.MessageBox('The age must be a number', 'ValueError', wx.OK | wx.ICON_ERROR)
        else:
            wx.MessageBox('Please fill all the values', 'ValueError', wx.OK | wx.ICON_ERROR)

    def on_click(self, event):
        self.make_the_log()


if __name__ == '__main__':
    # Start the App MainLoop
    try:
        log = LogFile()
        if not os.path.isfile("ApplicationExternals\\LOGFILE"):
            app = wx.App()
            frame = User_Info(None, style=wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX) & wx.NO_BORDER)
            frame.Show()
            app.MainLoop()
        gui = DiagnostifyApp()
        gui.run()
    except ctypes.ArgumentError:
        gui.stop()
    except Exception:
        traceback.print_exc()
        input()
