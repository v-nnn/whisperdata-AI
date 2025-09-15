import csv

with open('test.csv', 'r') as file:
    reader = csv.reader(file)
    # Calculate number of rows in csv. Add this feature later.
    
    # Store the header seperately
    header = next(reader)

    # Initialize list for appending rows
    data = []

    row_count = 0

    # If more than 20 rows, append only the first 20. Else, append all of them (if less/equal to than 20 rows)
    for row in reader:
        data.append(row)
        row_count += 1
        if row_count >= 20:
            break


print(data)
