from django.http import HttpResponse


class IgnoreStaticFilesMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        blocked_files = ["owl.video.play.html", "nouislider.css"]
        if any(file in request.path for file in blocked_files):
            return HttpResponse(status=404)
        return self.get_response(request)
