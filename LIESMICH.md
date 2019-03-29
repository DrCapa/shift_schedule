# Schichtplan
Ein Fachbereich einer Firma mit 8 Mitarbeitern arbeitet im 3-Schicht-Betrieb (früh, mittel, spät). Gesucht ist ein Schichtplan für einen vorgegeben Zeitraum (z.B. Woche oder Monat) unter den folgenden Bedingungen:
* Maximale Anzahl Schichten pro Arbeiter,
* Minimale Anzahl Schichten pro Arbeiter,
* Maximale Anzahl aufeinander folgender Schichten,
* Minimale Anzahl aufeinander folgender Schichten gleicher Art,
* Minimale Anzahl zusammenhängender freier Tage,
* Nur eine Schicht pro Tag,
* Keine Frühschiht nach einer Spätschicht.

Weiterhin sind
* die Anzahl der benötigten Arbeiter pro Schicht und Tag,
* die Urlaubsplanung aus der Personalverwaltungssoftware (als csv-Export) und
* die Schichtwünsche der Mitarbeiter (als Exceltabelle)

gegeben.

Berechnet wird ein Schichtplan mit der maximalen Anzahl an berücksichtigten Schichtwünschen unter Einhaltung aller oben genannten Nebenbedingungen. In der Ausgabe befindet sich zudem eine Überischt der verschiedenen Schichten und freien Tage pro Arbeiter.

Weiterführend können zusätzliche Bedingungen wie

* Einhaltung der Schichtreihenfolge Früh-Mittel-Spät-Frei,
* maximale Anzahl aufeinander folgender Schichten gleicher Art,
* Berücksichtigung des vorangegangenen Zeitraumes

und andere berücksichtigt werden. 