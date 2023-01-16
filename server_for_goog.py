from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/prime', methods=['POST'])
def switch():
	pass
	query = request.json.get('obj',"NA")
	
print(query, 'query')

if __name__ == '__main__':
    app.run(host= '0.0.0.0',debug=True,port=80)
