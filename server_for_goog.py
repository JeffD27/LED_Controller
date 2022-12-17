from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/prime', methods=['POST'])
def switch():
    query = request.json.get('obj',"NA")
    # Process query and turn appliance on/off with RPi.GPIO


if __name__ == '__main__':
    app.run(host= '0.0.0.0',debug=True,port=8000)
