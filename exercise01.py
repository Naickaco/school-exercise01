import RPi.GPIO as GPIO
import time
import logging
import sqlite3
import os
import os.path

class Led:
	def __init__(self, pin : int):
		self.__pin = pin
		self.__state = False
		self.__Setup()

	def __Setup(self):
		GPIO.setup(self.__pin, GPIO.OUT)

	def __Update(self):
		GPIO.output(self.__pin, self.__state)
	
	def show(self):
		self.__state = True
		self.__Update()
	
	def hide(self):
		self.__state = False
		self.__Update()

	def toggle(self):
		self.__state = not self.__state
		self.__Update()

	def get_state(self) -> bool:
		return self.__state

class Taster:
	def __init__(self, pin : int):
		self.__pin = pin
		self.__Setup()
	
	def __Setup(self):
		GPIO.setup(self.__pin, GPIO.IN)
	
	def is_pressed(self):
		return GPIO.input(self.__pin)

class LoopHandler:
	BASE_DIR = os.path.dirname(os.path.abspath(__file__))

	def __init__(self):
		GPIO.setmode(GPIO.BOARD)
		self.__taster = Taster(11)
		self.__led = Led(7)
		self.__led.hide()
		self.__currentState = False
		self.__startTime = 0
		
		self.__database = sqlite3.connect(os.path.join(self.BASE_DIR, "worker.db"))
		# Create table
		self.c = self.__database.cursor()
		with open(os.path.join(self.BASE_DIR, "setup.sql"), 'r') as sql_file:
			self.c.executescript(sql_file.read())

		self.__database.commit()

	def onSave(self, state : bool):
		c = self.__database.cursor()
		if state:
			s = "AN"
		else:
			s = "Aus"
		self.c.execute("""
			INSERT INTO led_zustand(zustand, time) VALUES('%s', datetime('now', 'localtime'));
		""" % (s))
		self.__database.commit()
	
	def Loop(self):
		try:
			while True:
				self.Update()
				time.sleep(0.1)
		except KeyboardInterrupt:
			GPIO.cleanup()
	
	def Update(self):
		s = not self.__taster.is_pressed()
  
		print("The taster state %d. self.__startTime -> %d self.__currentState : %d" % (s, self.__startTime, self.__currentState))
		if s:  
			if not self.__currentState:
				self.__startTime = time.time()
				self.__currentState = True
		elif not s:
			if self.__currentState:
				record_time = time.time() - self.__startTime
				print("reclap record_time = ", record_time)
				if record_time <= 0.5:
					self.__led.toggle()
					self.onSave(self.__led.get_state())
				self.__currentState = False
				self.__startTime = 0
    

			


if __name__ == "__main__":
	LoopHandler().Loop()
