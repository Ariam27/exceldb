import csv
from operator import delitem

with open("example_database/cars.csv", "r") as f:
    reader = csv.reader(f, delimiter=",")
    while input("Quit? ") != "y":
        print(next(reader))
