from flask import Flask, request

app = Flask(__name__)

@app.route("/",methods=['POST','GET'])
def mainm():
    if request.method=='POST':
        #Retrieve the data_id submitted by the user. Get the data corresponding 
        # to this id and return it back to the user.
        record = request.get_json()['data_id'] 

        return "This is the data corresponding to data id: " + str(record)
    else:
        return "maindb.py - This is get method - try using post -- " 

if __name__=="__main__":
    app.run(host='0.0.0.0', port=8082, debug=True)  