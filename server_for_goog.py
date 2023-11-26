from flask import Flask
from flask_restful import Api, Resource, reqparse
import os


app = Flask(__name__)
api = Api(app)

class Action(Resource):
	def post(self, name):
		print('working')
		if(name == "backgroundlightsorange"):
			print('rebooting!')
			os.system("reboot")    
        
	def get(self, name):
		print('here')
		return  name
api.add_resource(Action, "/action/<name>")
if __name__ == '__main__':
	
	app.run(host= '0.0.0.0',debug=True)
