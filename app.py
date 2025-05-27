import mimetypes
import os
import uuid
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs

from PIL import Image
import io
import json

import logging

IMAGES_DIR = os.path.join(os.getcwd(), "images")
LOGS_DIR = os.path.join(os.getcwd(), "logs")

os.makedirs(IMAGES_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

logging.basicConfig(
    filename=os.path.join(LOGS_DIR, 'app.log'),
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 МБ

HOST = '0.0.0.0'
PORT = 8000


class AppHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        logging.info(f"do_GET: начало обработки пути {self.path}")
        if self.path == '/':
            logging.info("do_GET: отправка index.html")
            self.serve_file("static/index.html", "text/html")

        elif self.path == '/upload':
            logging.info("do_GET: отправка upload.html")
            self.serve_file("static/upload.html", "text/html")

        elif self.path == '/gallery':
            try:
                logging.info("do_GET: формирование страницы галереи")
                files = [f for f in os.listdir(IMAGES_DIR) if f.lower().endswith(('.jpg', '.png', '.gif'))]

                html = '''
                    <!DOCTYPE html>
                    <html lang="ru">
                    <head>
                        <meta charset="UTF-8">
                        <title>Галерея</title>
                        <link rel="stylesheet" href="/static/styles.css">
                    </head>
                    <body>
                        <header><h1>Загруженные изображения</h1></header>
                        <div class="container gallery">
                '''
                for file in files:
                    html += f'''
                        <div class="gallery-item">
                            <a href="/images/{file}" target="_blank">
                                <img src="/images/{file}" alt="{file}" style="max-width:200px; max-height:200px;">
                            </a>
                            <p>{file}</p>
                        </div>
                    '''

                html += '''
                        </div>
                        <div class="links">
                            <a href="/">На главную</a> | <a href="/upload">Загрузить ещё</a>
                        </div>
                    </body></html>
                '''

                self.send_response(200)
                self.send_header("Content-type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(html.encode("utf-8"))
                logging.info("do_GET: страница галереи отправлена")
            except Exception as e:
                logging.error(f"do_GET: Ошибка при формировании галереи: {e}")
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))

        elif self.path == '/images/list':
            try:
                files = [
                    {"name": f, "url": f"/images/{f}"}
                    for f in os.listdir(IMAGES_DIR)
                    if f.lower().endswith(('.jpg', '.png', '.gif'))
                ]
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(files).encode("utf-8"))
                return
            except Exception as e:
                logging.error(f"Ошибка в /images/list: {e}")
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
                return

            except Exception as e:
                logging.error(f"do_GET: Ошибка при формировании галереи: {e}")
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
                return

        elif self.path.startswith('/images/'):
            filename = self.path[len("/images/") :]
            logging.info(f"do_GET: запрос изображения {filename}")
            if '..' in filename or '/' in filename or '\\' in filename:
                logging.warning(f"do_GET: недопустимое имя файла: {filename}")
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Недопустимое имя файла"}).encode("utf-8"))
                return
            filepath = os.path.join(IMAGES_DIR, filename)
            if os.path.isfile(filepath):
                mime_type, _ = mimetypes.guess_type(filepath)
                mime_type = mime_type or "application/octet-stream"
                self.send_response(200)
                self.send_header("Content-Type", mime_type)
                self.end_headers()
                with open(filepath, "rb") as f:
                    self.wfile.write(f.read())
                logging.info(f"do_GET: изображение {filename} отправлено")
                return
            else:
                logging.warning(f"do_GET: файл не найден {filename}")
                self.send_response(404)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Файл не найден."}).encode("utf-8"))
                return

        elif self.path == '/images/':
            try:
                files = [f for f in os.listdir(IMAGES_DIR) if f.lower().endswith(('.jpg', '.png', '.gif'))]
                logging.info(f"do_GET: список изображений запрошен, найдено {len(files)} файлов.")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()

                html = "<html><body><h2>Список изображений:</h2><ul>"
                for f in files:
                    html += f"<li><a href='/images/{f}' target='_blank'>{f}</a></li>"
                html += "</ul></body></html>"
                self.wfile.write(html.encode("utf-8"))
                return
            except Exception as e:
                logging.error(f"do_GET: Ошибка при получении списка изображений: {e}")
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
                return

        elif self.path.startswith('/static/'):
            file_path = self.path.lstrip('/')
            if os.path.isfile(file_path):
                logging.info(f"do_GET: отправка статического файла {file_path}")
                self.send_response(200)
                mime_type, _ = mimetypes.guess_type(file_path)
                self.send_header('Content-type', mime_type or 'application/octet-stream')
                self.end_headers()
                with open(file_path, 'rb') as f:
                    self.wfile.write(f.read())
                return
            else:
                logging.warning(f"do_GET: статический файл не найден {file_path}")
                self.send_response(404)
                self.end_headers()
                return

        else:
            logging.warning(f"do_GET: неизвестный путь {self.path}")
            self.send_response(404)
            self.end_headers()
            return

    def do_POST(self):
        logging.info(f"do_POST: начало обработки пути {self.path}")
        if self.path == '/upload':
            logging.info("do_POST: начало обработки загрузки файла")
            content_length = int(self.headers.get('Content-Length', 0))
            content_type = self.headers.get('Content-Type')
            logging.debug(f"do_POST: Content-Type: {content_type}")

            if not content_type or "multipart/form-data" not in content_type:
                logging.error("do_POST: ошибка - неверный Content-Type")
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Неверный Content-Type"}).encode('utf-8'))
                return

            boundary = content_type.split("boundary=")
            if len(boundary) < 2:
                logging.error("do_POST: ошибка - неверный boundary")
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Неверный boundary"}).encode('utf-8'))
                return
            boundary = boundary[1].strip('"').encode()
            logging.debug(f"do_POST: Boundary: {boundary}")

            body = self.rfile.read(content_length)
            logging.debug(f"do_POST: Body length: {len(body)}")
            parts = body.split(b"--" + boundary)
            logging.debug(f"do_POST: Parts count: {len(parts)}")

            for i, part in enumerate(parts):
                logging.debug(f"do_POST: Part {i} length: {len(part)}")

            for part in parts:
                if b'Content-Disposition' in part and b'name="file"' in part:
                    try:
                        headers, file_data = part.split(b"\r\n\r\n", 1)
                        file_data = file_data.rstrip(b"\r\n--")
                    except Exception as e:
                        logging.error(f"do_POST: ошибка обработки файла: {e}")
                        self.send_response(400)
                        self.send_header('Content-Type', 'application/json')
                        self.send_header('Access-Control-Allow-Origin', '*')
                        self.end_headers()
                        self.wfile.write(json.dumps({"error": f"Ошибка обработки файла: {e}"}).encode('utf-8'))
                        return

                    logging.debug(f"Размер полученного файла: {len(file_data)} байт")
                    if len(file_data) > MAX_FILE_SIZE:
                        logging.warning("do_POST: файл слишком большой")
                        self.send_response(400)
                        self.end_headers()
                        self.wfile.write(json.dumps({"error": "Файл слишком большой. Максимум 5 МБ."}).encode("utf-8"))
                        return

                    try:
                        image = Image.open(io.BytesIO(file_data))
                        image.verify()
                    except Exception as e:
                        logging.warning(f"do_POST: файл не является изображением: {e}")
                        self.send_response(400)
                        self.send_header('Content-Type', 'application/json')
                        self.send_header('Access-Control-Allow-Origin', '*')
                        self.end_headers()
                        self.wfile.write(json.dumps({"error": "Файл не является допустимым изображением."}).encode("utf-8"))
                        return

                    header_str = headers.decode("utf-8", errors="ignore")
                    filename_marker = 'filename="'
                    original_filename = ""
                    if filename_marker in header_str:
                        original_filename = header_str.split(filename_marker)[-1].split('"')[0]
                        ext = os.path.splitext(original_filename)[-1].lower()
                    else:
                        ext = ""

                    if ext not in {'.jpg', '.png', '.gif'}:
                        logging.error(f"do_POST: ошибка - неподдерживаемый формат файла ({original_filename}).")
                        self.send_response(400)
                        self.send_header('Content-Type', 'application/json')
                        self.send_header('Access-Control-Allow-Origin', '*')
                        self.end_headers()
                        self.wfile.write(json.dumps({"error": "Ошибка: неподдерживаемый формат файла."}).encode("utf-8"))
                        return

                    filename = f"{uuid.uuid4()}{ext}"
                    filepath = os.path.join(IMAGES_DIR, filename)
                    os.makedirs(IMAGES_DIR, exist_ok=True)
                    try:
                        with open(filepath, "wb") as f:
                            f.write(file_data)
                        logging.info(f"do_POST: успех - изображение {filename} ({len(file_data)} байт) загружено.")
                    except Exception as e:
                        logging.error(f"do_POST: ошибка записи файла: {e}")
                        self.send_response(500)
                        self.send_header('Content-Type', 'application/json')
                        self.send_header('Access-Control-Allow-Origin', '*')
                        self.end_headers()
                        self.wfile.write(json.dumps({"error": "Ошибка при сохранении файла."}).encode('utf-8'))
                        return

                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    host = self.headers.get("Host", f"{HOST}:{PORT}")
                    image_url = f"http://{host}/images/{filename}"
                    self.wfile.write(json.dumps({"url": image_url}).encode("utf-8"))
                    return

            logging.error("do_POST: ошибка - файл не найден в запросе")
            self.send_response(400)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Файл не найден в запросе"}).encode("utf-8"))
            return

        elif self.path == '/delete-image':
            logging.info("do_POST: начало обработки удаления изображения")
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            params = parse_qs(post_data.decode('utf-8'))
            filename = params.get('filename', [None])[0]
            if not filename or '..' in filename or '/' in filename or '\\' in filename:
                logging.error(f"do_POST: ошибка - недопустимое имя файла для удаления: {filename}")
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Недопустимое имя файла для удаления"}).encode("utf-8"))
                return
            if os.path.isfile(os.path.join(IMAGES_DIR, filename)):
                filepath = os.path.join(IMAGES_DIR, filename)
                if os.path.isfile(filepath):
                    try:
                        os.remove(filepath)
                        logging.info(f"do_POST: удаление - изображение {filename} удалено.")
                        self.send_response(200)
                        self.send_header('Access-Control-Allow-Origin', '*')
                        self.end_headers()
                        self.wfile.write("Файл удалён".encode("utf-8"))
                        return
                    except Exception as e:
                        logging.error(f"do_POST: ошибка удаления файла: {e}")
                        self.send_response(500)
                        self.send_header('Content-Type', 'application/json')
                        self.send_header('Access-Control-Allow-Origin', '*')
                        self.end_headers()
                        self.wfile.write(json.dumps({"error": f"Ошибка удаления: {e}"}).encode('utf-8'))
                        return
                else:
                    logging.warning(f"do_POST: файл для удаления не найден: {filename}")
                    self.send_response(404)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "Файл не найден"}).encode("utf-8"))
                    return

        else:
            logging.warning(f"do_POST: неизвестный путь {self.path}")
            self.send_response(404)
            self.end_headers()
            return

    def serve_file(self, filepath, content_type):
        logging.info(f"serve_file: попытка отправить файл {filepath} с типом {content_type}")
        try:
            with open(filepath, 'rb') as f:
                self.send_response(200)
                self.send_header('Content-type', content_type)
                self.end_headers()
                self.wfile.write(f.read())
            logging.info(f"serve_file: файл {filepath} успешно отправлен")
        except FileNotFoundError:
            logging.error(f"serve_file: файл не найден {filepath}")
            self.send_response(404)
            self.end_headers()
            return


def run():
    print("DEBUG: Запуск сервера с логированием...")
    logging.info("DEBUG: Запуск сервера с логированием...")
    if not os.access(IMAGES_DIR, os.W_OK):
        logging.error(f"Ошибка: Нет прав на запись в папку {IMAGES_DIR}")
    else:
        logging.info(f"Права на запись в папку {IMAGES_DIR} подтверждены")
    print("Сервер запускается...")
    server = HTTPServer((HOST, PORT), AppHandler)
    print(f"Сервер слушает на {HOST}:{PORT}")
    server.serve_forever()


if __name__ == '__main__':
    run()