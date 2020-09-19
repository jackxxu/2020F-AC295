from flask import Flask,render_template, request
import sys
import requests

app = Flask(__name__)

@app.route("/",methods=['POST','GET'])
def mainm():
      if request.method=='POST':  # User clicked submit button        
        data_id = request.form['dataidname'] 
        # send this data_id to maindb.py         
        resp = requests.post(url=db_url,json={'data_id':data_id})
        return resp.content
      else:
        return  render_template('index.html') 

if __name__=="__main__":
    # determine what the URL for the database should be, port is always 8082 for DB
    if(len(sys.argv) == 2):
        db_url = 'http://' + sys.argv[1] + ':8082'
    else:
        db_url = "http://0.0.0.0:8082/"  
   
    app.run(host='0.0.0.0', port=8081, debug=True)	