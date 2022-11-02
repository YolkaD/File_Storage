
import json
import uuid
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse
import datetime
import magic


from FileStorageDatabase import Data_Base

class RequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path.startswith('/api/get'):
            params = parse_qs(urlparse(self.path).query)
            count = 0
            for k, v in params.items():
                if k in ['id', 'name', 'tag', 'size', 'mimeType', 'modificationTime']:
                    count += 1
            if count == 0:
                database = Data_Base()
                self.send_response(200)
                self.end_headers()
                json_obj = json.dumps(database.loading_all(), indent=4)
                self.wfile.write(json_obj.encode('utf-8'))
            else:
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                data_base = Data_Base()
                json_obj = json.dumps(data_base.loading_by_params(params), indent=4)
                self.wfile.write(json_obj.encode('utf-8'))
        elif self.path.startswith('/api/download'):
            params = parse_qs(urlparse(self.path).query)
            if 'id' in params:
                id = str(params['id'][0])
                database = Data_Base()
                if database.loading_by_id(id):
                    data = database.loading_by_id(id)
                    print(data)
                    print(data[0]["mimeType"])
                    self.send_response(200)
                    self.send_header('Content-Type', data[0]["mimeType"])
                    self.send_header('Content-Disposition: attachment; filename=', data[0]['name'])
                    self.send_header('Content-Length', str(int(data[0]['size'])))
                    self.end_headers()
                    with open(id, mode="rb") as body:
                        content = body.read()
                        self.wfile.write(content)
                else:
                    self.send_response(404)
                    self.end_headers()
                    self.wfile.write('файл не существует'.encode('utf-8'))
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write('отсутствуют условия'.encode('utf-8'))
        else:
            self.send_response(501)
            self.end_headers()
            self.wfile.write('Not Implemented'.encode('utf-8'))

    def do_POST(self):
        if self.path.startswith('/api/upload'):
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            mimeType = magic.from_buffer(body, mime=True)
            params = parse_qs(urlparse(self.path).query)
            now = datetime.datetime.now()
            modificationTime = now.strftime("%Y-%m-%d %H:%M:%S")
            if 'id' in params:
                id = params['id'][0]
            else:
                id = str(uuid.uuid4())
            if 'name' in params:
                name = params['name'][0]
            else:
                name = id
            if 'tag' in params:
                tag = params['tag'][0]
            else:
                tag = ''

            file_dict = {
                'id': id,
                'name': name,
                'tag': tag,
                'size': content_length,
                'mimeType': mimeType,
                'modificationTime': modificationTime
            }
            database = Data_Base()
            if database.loading_by_id(id):
                database.update(file_dict)
            else:
                database.save_in_table(file_dict)
            with open(id, mode="wb") as file:
                file.write(body)
            self.send_response(201)
            self.send_header('Content-Type', 'multipart/form-data')
            self.end_headers()
            json_obj = json.dumps(file_dict, indent=4)
            self.wfile.write(json_obj.encode('utf-8'))
        else:
            self.send_response(501)
            self.end_headers()
            self.wfile.write('Not Implemented'.encode('utf-8'))

    def do_DELETE(self):
        if self.path.startswith('/api/delete'):
            params = parse_qs(urlparse(self.path).query)
            count = 0
            for k, v in params.items():
                if k in ['id', 'name', 'tag', 'size', 'mimeType', 'modificationTime']:
                    count += 1
            if count == 0:
                self.send_response(400)
                self.end_headers()
                self.wfile.write("отсутствуют условия".encode('utf-8'))
            else:
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                data_base = Data_Base()
                count = data_base.delete(params)
                result = f"{count} files deleted"
                self.wfile.write(result.encode('utf-8'))
        else:
            self.send_response(501)
            self.end_headers()
            self.wfile.write('Not Implemented'.encode('utf-8'))


if __name__ == '__main__':
    server = HTTPServer(("127.0.0.1", 9680), RequestHandler)
    print('Сервер активен')
    server.serve_forever()










