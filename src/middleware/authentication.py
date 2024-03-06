# from fastapi import Request
#
#
# def add_check_request_signature_middleware(app):
#     # @app.middleware("http")
#     async def check_request_signature(request: Request, call_next):
#         """
#         Should exist an implemented method here to verify the digital
#         signature that comes with the request. But since it is not passed
#         the Access-Time. It is no possible mount the message.
#         :param request:
#         :param call_next:
#         :return:
#         """
#
#         response = await call_next(request)
#         return response
