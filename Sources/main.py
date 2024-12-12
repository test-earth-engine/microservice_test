from flask import Flask, request


app = Flask("internal")


@app.route('/workflow_dispatch/<string:id>', methods=['GET', 'POST'])
def users(id):
    print(id)
    return id, 200


def cloud_function(request):
    internal_ctx = app.test_request_context(path=request.full_path,
                                            method=request.method)
    
    internal_ctx.request.data = request.data
    internal_ctx.request.headers = request.headers
    
    internal_ctx.push()
    return_value = app.full_dispatch_request()

    internal_ctx.pop()
    return return_value

"""
SEE:
https://medium.com/google-cloud/use-multiple-paths-in-cloud-functions-python-and-flask-fc6780e560d3
"""