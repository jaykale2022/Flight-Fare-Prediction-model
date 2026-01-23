
# accessing the built-in functions  i.e. library
import mysql.connector as conn
from sklearn.linear_model import LinearRegression
import pandas as pd

#extracting the data from the dataset in csv format
filep="C:/Users/Jay/Desktop/potential jobs/FF-ML/flight_data_BOM_NWD.csv"

df= pd.read_csv(filep)
print(df.head())
#creating a linear regression model that helps in predicting new values or inputs
reg = LinearRegression()


#creating a multi-dimensional list and finding the count of the price attribute
a=list()
arr=tuple(df['Price'])
lstI=arr.index(10711)
print(lstI)


for i in range(1,lstI):
  df['Duration'][i]=int(df['ArrivingTime'][i])-int(df['DepartingTime'][i])

reg.fit(df[['DepartingTime','ArrivingTime','Duration']],df[['Price']])
print(reg.score(df[['DepartingTime','ArrivingTime','Duration']],df[['Price']])*100)

new=list()
new.extend([list(map(int,input("enter departing and arriving times").split()))])
print(new)

print(reg.predict([[new[0][0],new[0][1],(new[0][1]-new[0][0])*60]]))


print(df['Duration'])
for i in range(1,lstI):
 if (( abs(df['DepartingTime'][i] - new[0][0] ))<= 4 )and (abs(int(df['DepartingTime'][i]))!=new[0][0] ) and ( abs(df['ArrivingTime'][i]- new[0][1] ) <= 4 ):
          diff=abs(reg.predict([[df['DepartingTime'][i],df['ArrivingTime'][i],df['Duration'][i]]])-reg.predict([[new[0][0],new[0][1],(new[0][1]-new[0][0])*60]] ))
          print(reg.predict([[new[0][0],new[0][1],(new[0][1]-new[0][0])*60]]))
          a.extend([[df['FlightName'][i],int(df['DepartingTime'][i]),int(df['ArrivingTime'][i]),int(diff)]])
print("Company, departure, arrival, cost benefits")
for i in range(0,len(a)):
 print(a[i])       
flight_details=list()
o=input("which flight do you want to take? type the name of the flight and book the flight corresponding to your particular time ")
for i in range(len(a)):
  if(a[i][0]==o):
    flight_details.extend([a[i][0],a[i][1],a[i][2],a[i][3],int(reg.predict([[a[i][1],a[i][2],(a[i][1]-a[i][2])*60]]))])

print("your flight details based on your choosen flight\n")         
for i in range(0,len(flight_details)):
 print(flight_details[i])           
              

    

               
    
# new1=[[float(17.50)],[float(21.5)],[float(240)]]
# print(reg.predict([[new[0][0],new[1][0],new[2][0]]]))
# print(reg.predict([[new1[0][0],new1[1][0],new1[2][0]]]))
# # Define the connection parameters
# config = {
#     'user': 'root',
#     'password': 'MySQL@2025',
#     'host': 'localhost',
#     'database': 'world'
# }

# # Establish the connection
# mydb=conn.connect(**config)


# # # Do something with the connection
# # print("Connection established!")
# cur = mydb.cursor()
# # created object of connector's method cursor and executed queries on the table flight_data 

# # sqlCreate = f"""
# #     CREATE TABLE {"flight_data1"} (
# #         x INT,
# #         y INT 
# #     )
# #     """


# # cur.execute(sqlCreate)
# mydb.commit()
# x=[[151],[174],[138],[186],[128],[136],[179],[163],[152],[131]]
# y=[[63],[81],[56],[91],[47],[57],[76],[72],[62],[48]]
# columns=dict()
# column=list()
# for i in range(0,len(x)):
#     columns[x[i][0]]=y[i][0]
# # print(columns)
# for pair in columns.keys():
#     column.append([pair,columns[pair]])
# # columnDS=tuple(column)
# print(column)

# # for c in columnDS:
# #     # print(c)
# #     sqlInsert = f"""INSERT INTO flight_data1 (x,y) VALUES ({c[0]},{c[1]});"""
# #     cur.execute(sqlInsert)
# #     mydb.commit()


# sqlSelect = f"""select * from flight_data1;"""
# cur.execute(sqlSelect)
# # mydb.commit()
# Result=cur.fetchall()
# print(Result)
# x1=[]
# y1=[]
# for i in range(0,len(Result)):
#     x1.append([Result[i][0]])
#     y1.append([Result[i][1]])

# model = LinearRegression()
# model.fit(x1,y1)

# print(model.score(x1,y1)*100)
# new=[[161]]
# print(model.predict(new)[0])