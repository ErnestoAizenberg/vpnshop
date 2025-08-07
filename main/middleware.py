class ClientTypeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Detect VPN clients
        # TO DO: Detect VPN clients

        request.client_type = "vpn" if False else "web"
        return self.get_response(request)
