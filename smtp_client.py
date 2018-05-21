from socket import *
import ssl
import base64
import conf
import os
import magic


def send(message, sock):
    sock.send(message + b"\r\n")
    result = sock.recv(1024).decode()
    if 'Error' in result:
        print(result)
        return None
    return result


def get_getters(list_getters):
    result = []
    for getter in list_getters:
        result.append('<' + getter + '>')
    return ", ".join(result)


def get_text_data():
    data = b''
    try:
        with open('source/' + conf.text_file, 'rb') as f:
            lines = f.readlines()
            for line in lines:
                if line[0] == 46:
                    data += b'.'
                data += line
    except:
        data = b'error '
    return data + b'\n'


def get_attachments(directory):
    b_data = b''
    mime = magic.Magic(mime=True)
    for file in os.listdir(directory):
        row_data = b''
        if file == conf.text_file:
            continue
        with open(directory + '/' + file, 'rb') as f:
            row_data = f.read()
        mime_type = mime.from_file(directory + '/' + file)
        b_data += get_body(file, mime_type, '--bound.49162.web12g.yandex.ru')
        b_data += base64.b64encode(row_data)
        b_data += b'\n\n'
    return b_data


def get_body(file_name, mime_type, delimiter):
    body = '''{0}
Content-Disposition: attachment; filename="{1}"
Content-Transfer-Encoding: base64
Content-Type: {2}; name"{1}"

'''.format(delimiter, file_name, mime_type)
    return body.encode()


def form_message_2():
    data = '''from: {2}
to: {0}
Subject: {1}
MIME-Version: 1.0
Content-Type: multipart/mixed; boundary="bound.49162.web12g.yandex.ru"

--bound.49162.web12g.yandex.ru
Content-Transfer-Encoding: 8bit
Content-Type: text/plain; charset=utf-8

'''.format(get_getters(conf.recipients), conf.topic, conf.login)

    end_data = '''
--bound.49162.web12g.yandex.ru--''' + '\n.\n'

    return data.encode() + get_text_data() + get_attachments('source') + end_data.encode()


def send_message():
    sock = socket()
    sock.settimeout(5)
    try:
        sock.connect(('smtp.yandex.ru', 465))
        sock = ssl.wrap_socket(sock, ssl_version=ssl.PROTOCOL_SSLv23)
    except:
        print('no connection, sorry')
        return

    send('EHLO {}'.format(conf.login).encode(), sock)
    send(b'AUTH LOGIN', sock)
    login = base64.b64encode(conf.login.encode())
    password = base64.b64encode(conf.password.encode())
    send(login, sock)
    send(password, sock)

    if send(b'MAIL FROM: ' + conf.login.encode(), sock) is None:
        sock.close()
        return
    for getter in conf.recipients:
        send(b'RCPT TO: ' + getter.encode(), sock)

    data = form_message_2()

    send(b'DATA', sock)
    send(data, sock)

    print('Email was sent')

    sock.close()


if __name__ == "__main__":
    send_message()
