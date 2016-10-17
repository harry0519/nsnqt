import csv

file_type  = ".csv"

def save_data_to_csv(file_name,data_set):
    print("Start to save data to csv")
    with open(file_name + file_type,"w",newline="") as datacsv:
	    csvwriter = csv.writer(datacsv,dialect = ("excel"))
	    csvwriter.writerow(data_set.Data)
       
    print("data have been saved to "+ file_name + file_type)
