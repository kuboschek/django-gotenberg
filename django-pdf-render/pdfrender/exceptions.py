import requests.exceptions

class RenderException(Exception):
    pass

class PDFServerException(RenderException):
    pass

class FileGatheringException(RenderException):
    pass