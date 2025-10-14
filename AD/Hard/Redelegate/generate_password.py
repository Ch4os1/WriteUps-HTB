from datetime import datetime

seasons= ['Spring','Summer','Fall','Winter']

for year in range(2000,datetime.now().year+1):
    for searson in seasons:
        with open ("passwords.txt", "a") as file:
            password = searson + str(year)+'!'
            file.write(password+"\n")
        print (searson + str(year)+'!')
