import RPi.GPIO as GPIO
import time
import logging
import sqlite3
import os
import os.path

class Led:
	def __init__(self, pin : int):
		"""
			Erstellt eine Led und registiert den pin als Ausgang. 
			Jede Led beinhaltet einen Status. Der Status gibt an ob die Led angeschaltet oder ausgeschaltet ist.

			Args:
				pin (int): An dem angegeben Pin wird die Led angeschlossen. 
		"""		
		self.__pin = pin
		self.__state = False
		self.__Setup()

	def __Setup(self):
		# Registiert den Pin von Objekt als Ausgang, damit die Led ein- und ausgeschaltet werden kann. 
		GPIO.setup(self.__pin, GPIO.OUT)

	def __Update(self):
		# Übermittelt den aktuellen Led Zustand zum Raspberry Pi.
		GPIO.output(self.__pin, self.__state)

	def show(self):
		# Schaltet den Zustand an und übergibt den Wert zur gleichen Zeit zum Raspberry Pi. 
		self.__state = True
		self.__Update()

	def hide(self):
		# Schaltet den Zustand aus und übergibt den Wert zur gleichen Zeit zum Raspberry Pi. 
		self.__state = False
		self.__Update()

	def toggle(self):
		# Negiert den Zustand und übergibt den Wert zur gleichen Zeit zum Raspberry Pi. 
		self.__state = not self.__state
		self.__Update()

	def get_state(self) -> bool:
		""" 
			Liefert den aktuellen Zustand der Led zurück. 

			Returns:
				bool: Greift auf state zu und liefert ihn zurück.  
		"""
		return self.__state

class Taster:
	def __init__(self, pin : int):
		""" 
			Erstellt eine Taster Instance und registiert den Taster als Eingabe. 

			Args:
				pin (int): Auf diesen Pin wird der Taster registiert. 
		"""

		self.__pin = pin
		self.__Setup()

	def __Setup(self):
		# Registiert den Taster als Eingang. 
		GPIO.setup(self.__pin, GPIO.IN)
	
	def is_pressed(self) -> bool:
		"""
			Überprüft ob ein Taster gedrückt wurde. 
	
			Returns:
				bool: returns if the taster is pressed.
		"""
		return not GPIO.input(self.__pin) # Bei meinen Button sind die Zustände verkehrt rum, darum das not.

class LoopHandler:
	BASE_DIR = os.path.dirname(os.path.abspath(__file__))

	def __init__(self):
		""" 
			Setzt den Modus von der Pin-Nummierung auf GPIO.BOARD.
			Erstellt jeweils eine Led, eine Taster instance und zwei Hilfsvariablen. Eine Hilfsvariable erfasst die Zeit wie lange der Taster gedrückt wurde.
			Die andere Hilfsvariable zeigt an ob der Taster schon mal gedrückt wurde oder losgelassen wurde (nur einmalig).
			Wenn keine Datebank vorhanden ist, wird eine Datenbank erstellt.
		"""
		GPIO.setmode(GPIO.BOARD)
		self.__taster = Taster(11)
		self.__led = Led(7)
		self.__led.hide()
		self.__currentState = False
		self.__startTime = 0.0
		
		self.__database = sqlite3.connect(os.path.join(self.BASE_DIR, "worker.db"))
		# Create table
		cursor = self.__database.cursor()
		with open(os.path.join(self.BASE_DIR, "setup.sql"), 'r') as sql_file:
			cursor.executescript(sql_file.read())

		self.__database.commit()

	def __onSave(self, state : bool):
		""" 
			Speichert den Stand der Leuchtdiode in der Datenbank. 

			Args:
				state (bool): Der Status der Leuchtdiode. 
		"""		
		cursor = self.__database.cursor()
		if state:
			s = "AN"
		else:
			s = "Aus"
		cursor.execute("""
			INSERT INTO led_zustand(zustand, time) VALUES('%s', datetime('now', 'localtime'));
		""" % (s))
		self.__database.commit()

	def __Update(self):
		"""
			Überprüft durchgehend ob der Taster gedrückt wurde, wenn ja 
			wird die aktuellen Zeit in einer Hilfsvariable gespeichert und auf ein Signal gewartet bis losgelassen wird.

			Sobald losgelassen wurde, wird wieder die aktuellen
			Zeit mit der davorherigen gedrückten Zeit subtrahiert um die Zeit zu errechnen,
			wie lange die der Taster gedrückt wurde.

			Wenn der Taster länger als 500 Millisekunden gedrückt wurde, wird der Zustand der Led negiert und in einer Datenbank-Tabelle festgehalten. 
		
			Am Ende werden alle Werte wieder zurückgesetzt.
		"""
		s = self.__taster.is_pressed()

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
					self.__onSave(self.__led.get_state())
				self.__currentState = False
				self.__startTime = 0.0

	def Loop(self):
		"""
			Führt die Schleife solange aus bis, sie Unterbrochen wird. 
		"""
		try:
			while True:
				self.__Update()
				time.sleep(0.1)
		except KeyboardInterrupt:
			GPIO.cleanup()
			self.__database.close()

if __name__ == "__main__":
	LoopHandler().Loop()
