import functions_framework


@functions_framework.http
def cloud_function(request):
    return 'Hello, World!'
