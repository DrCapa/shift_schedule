# Shift Schedule
We consider a department of a company with 8 workers and 3 shifts (early, middle, late). The aim is to create a shift schedule for a given periode (e.g. week or month) with the following constraints:

* Maximal shifts per worker,
* Minimal shifts per worker,
* Maximal sequence of shifts,
* Minimal sequence of same shifts,
* Minimal sequence of free days,
* Only one shift per day,
* No early shift after a late shift.

Also given are 
* the number of worker per shift and day,
* the vacation planning as csv-export of the personnel management tool and
* the shift requests of the worker (as a excel table).

The result of the optimization is a shift schedule with maximal shift requests subject to constraints. Finally you will get a overview of the different shifts and free days per worker.

Further more features like

* following the sequence early-middle-late-free,
* maximal sequence of same shifts,
* history of the privious periode

and other can be considered. 