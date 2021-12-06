from flask import Flask, request, Response
from distribute_challenge import object_to_string, b64_to_object

# Some security concerns: no checks on pickled object (check it is an expected function), no checks on user (could add secret key), no encryption/check to make sure instructions not tampered (use HTTPS or encryption)

app = Flask(__name__)

@app.route("/", methods=['POST'])
def main():
    # get object representation of function + args from request
    compute_obj = request.form['func']
    print(compute_obj)
    # reverse all encodings and unpickle to object representing function 
    compute_obj = compute_obj.encode('utf-8')
    compute_obj = b64_to_object(compute_obj)

    # run function contained in object with arguments
    output = compute_obj.func(*compute_obj.args, **compute_obj.kwargs)

    # since function could output any object, pickle and encode to string for response to client
    output_utf8 = object_to_string(output)

    return Response(output_utf8)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')

# Stand alone server start using : gunicorn -c gunicorn_config.py  --pid pidfile --bind 0.0.0.0:6000 --workers 10 --threads 1  --timeout 120 flask_server:app