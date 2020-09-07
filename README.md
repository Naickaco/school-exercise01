# LED und Taster

Eine Aufgabe um die Grundlagen wie Taster und Leuchtdioden zu wiederholen.
**Klasse: ITA18a**
**Schüler: CO**

## Aufgabe
Planen und Realisieren Sie eine Schaltung bestehend aus einer LED (mit Vorwiderstand) und einem Taster (mit Pull-down-Widerstand) an GPIO-Pins des Raspberry Pi. Die Anwendung soll wie folgt funktionieren:
* Wird der Taster kurz betätigt, wird die LED eingeschaltet und ein Zeitstempel und der Zustand der LED in einerDatenbanktabelle hinterlegt
* Wird der Taster ein zweites Mal kurz betätigt, wird die LED wieder ausgeschaltet. Auch hier erfolgtein Eintrag in der Datenbank. 
* Wird der Taster dauerhaft betätigt, so ändert sich der Zustand der LED nicht. 

## Lösung
[aufgabe-01](exercise01.py)

[Technische Berufliche Schule 1](http://tbs1.de/jcms/index.php)
