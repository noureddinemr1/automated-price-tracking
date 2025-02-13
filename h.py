import csv
import pandas

file_path = "itineraries.csv"  # Replace with your file path

with open(file_path, newline="", encoding="utf-8") as csvfile:
    reader = csv.reader(csvfile)
    print(pandas.DataFrame(reader))
