from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Mengirim respons sukses (200 OK)
        self.send_response(200)
        # Menentukan tipe konten adalah JSON
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        # Membuat pesan JSON untuk dikirim
        message = {'status': 'healthy', 'service': 'Simple Vercel Handler'}
        
        # Menulis pesan ke body respons
        self.wfile.write(json.dumps(message).encode('utf-8'))
        return
