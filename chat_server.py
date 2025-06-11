import socket
import threading
import time
import json

class ChatServer:
    def __init__(self, host='0.0.0.0', port=5555):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        self.clients = []
        self.nicknames = []
        print(f"서버가 {self.host}:{self.port}에서 시작되었습니다.")

    def broadcast(self, message, sender_socket=None):
        for client in self.clients:
            # 모든 클라이언트에게 메시지 전송 (보낸 사람 포함)
            try:
                client.send(message)
            except:
                # 연결이 끊긴 클라이언트 처리
                index = self.clients.index(client)
                self.clients.remove(client)
                client.close()
                nickname = self.nicknames[index]
                self.broadcast(f'{nickname} 님이 퇴장했습니다.'.encode('utf-8'))
                self.nicknames.remove(nickname)
                # 사용자 목록 업데이트 전송
                self.send_user_list()

    def handle_client(self, client_socket, nickname):
        while True:
            try:
                message = client_socket.recv(1024)
                if message:
                    print(f"{nickname}: {message.decode('utf-8')}")
                    self.broadcast(f"{nickname}: {message.decode('utf-8')}".encode('utf-8'), client_socket)
                else:
                    # 빈 메시지는 연결 종료를 의미
                    raise Exception("클라이언트 연결 종료")
            except:
                index = self.clients.index(client_socket)
                self.clients.remove(client_socket)
                client_socket.close()
                nickname = self.nicknames[index]
                self.broadcast(f'{nickname} 님이 퇴장했습니다.'.encode('utf-8'))
                self.nicknames.remove(nickname)
                # 사용자 목록 업데이트 전송
                self.send_user_list()
                break

    def send_user_list(self):
        """모든 클라이언트에게 현재 접속 중인 사용자 목록을 전송"""
        user_list = json.dumps({"type": "user_list", "users": self.nicknames})
        for client in self.clients:
            try:
                client.send(f"USER_LIST:{user_list}".encode('utf-8'))
            except:
                pass
    
    def run(self):
        while True:
            client_socket, address = self.server_socket.accept()
            print(f"연결 성공: {address}")
            
            # 클라이언트에게 닉네임 요청
            client_socket.send('NICK'.encode('utf-8'))
            nickname = client_socket.recv(1024).decode('utf-8')
            
            self.nicknames.append(nickname)
            self.clients.append(client_socket)
            
            print(f"{nickname} 님이 입장했습니다.")
            self.broadcast(f"{nickname} 님이 입장했습니다.".encode('utf-8'))
            client_socket.send('서버에 연결되었습니다!'.encode('utf-8'))
            
            # 사용자 목록 업데이트 전송
            self.send_user_list()
            
            # 클라이언트 처리를 위한 스레드 시작
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket, nickname))
            client_thread.daemon = True
            client_thread.start()

if __name__ == "__main__":
    server = ChatServer()
    server.run()