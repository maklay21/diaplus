from django.shortcuts import redirect
from django.shortcuts import render


class AdminProtectionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated and not request.user.is_staff:
            if request.path.startswith((
                '/admin/',
                '/product/add/',
                '/product/edit/',
                '/product/delete/',
                '/add-manufacturer/',
                '/add-product-type/'
            )):
                return render(request, 'pages/404.html', status=404)

        return self.get_response(request)


class CustomErrorMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if response.status_code in (404, 405):
            return render(request, 'pages/404.html', status=404)
        #elif response.status_code >= 500:
         #   context = {'error_code': response.status_code}
          #  return render(request, 'pages/5xx.html', context, status=response.status_code)

        return response
