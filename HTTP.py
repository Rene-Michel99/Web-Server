import datetime

class HTTPpackage:
    def __init__(self):
        pass

    def get_ok_template(self):
        data = "\r\nHTTP/1.1 200 OK\r\n"
        data += "Data: "+datetime.datetime.now().strftime('%d/%m/%Y %H:%M')+"\r\n"
        data += "Server: PYServidorWeb\r\n"
        data += "Content-Type: text/html\r\n"
        data += "\r\n"

        return data

    def get_error_template(self):
        data = "HTTP/1.1 404 NOT FOUND\r\n"
        data += "Data: "+datetime.datetime.now().strftime('%d/%m/%Y %H:%M')+"\r\n"
        data += "Server: PYServidorWeb\r\n"
        data += "Content-Type: text/html\r\n"
        data += "\r\n"
        data += "<html><body><h1>ERROR 404 NOT FOUND</h1></body></html>\r\n\r\n"

        return data

    def get_css_template(self):
        data = "\r\nHTTP/1.1 200 OK\r\n"
        data += "Data: "+datetime.datetime.now().strftime('%d/%m/%Y %H:%M')+"\r\n"
        data += "Server: ServidorWeb\r\n"
        data += "Content-Type: stylesheet\r\n"
        data += "\r\n"

        return data

    def get_js_template(self):
        data = "\r\nHTTP/1.1 200 OK\r\n"
        data += "Data: "+datetime.datetime.now().strftime('%d/%m/%Y %H:%M')+"\r\n"
        data += "Server: ServidorWeb\r\n"
        data += "Content-Type: application/javascript\r\n"
        data += "\r\n"

        return data

    def get_img_template(self):
        data = "\r\nHTTP/1.1 200 OK\r\n"
        data += "Data: "+datetime.datetime.now().strftime('%d/%m/%Y %H:%M')+"\r\n"
        data += "Server: ServidorWeb\r\n"
        data += "Content-Type: image/png\r\n"
        data += "\r\n"

        return data

    def get_template(self,path):
        if path.find('.css') != -1:
            return self.get_css_template()
        elif path.find('.png') != -1 or path.find('.jpg') != -1:
            return self.get_img_template()
        elif path.find('.js') != -1:
            return self.get_js_template()
        else:
            return self.get_ok_template()
