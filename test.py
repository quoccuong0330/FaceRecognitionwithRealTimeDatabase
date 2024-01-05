import csv
import os

from datetime import date

# Compute the local datetime: local_dt


# Print the local datetime
local_dt = date.today()
dir = 'Excel'
if not os.path.exists(dir):
    os.mkdir(dir)

pathList = os.listdir(dir)
# for path in pathList:

with open(os.path.join(dir, str(local_dt)+".csv"), mode="r+") as csvfile:
    fieldnames = ['fis','last']
    writer = csv.DictWriter(csvfile,fieldnames=fieldnames)
    writer.writeheader()
    writer.writerow({"fis":"3","last":"2"})