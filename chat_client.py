import pygame
import socket
import threading
import sys
import json

# Pygame 초기화
pygame.init()

# 화면 설정
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("실시간 채팅 프로그램")

# 색상 정의
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
LIGHT_BLUE = (173, 216, 230)
LIGHT_GREEN = (200, 255, 200)

# 폰트 설정 - 한글 지원을 위한 폰트 설정
# 맑은 고딕 폰트 파일 직접 지정
try:
    # 맑은 고딕 폰트 직접 지정
    font = pygame.font.Font("C:\\Windows\\Fonts\\malgun.ttf", 20)
    small_font = pygame.font.Font("C:\\Windows\\Fonts\\malgun.ttf", 16)
    print("맑은 고딕 폰트 로드 성공")
except Exception as e:
    print(f"폰트 로드 오류: {e}")
    # 기본 폰트 사용
    font = pygame.font.Font(None, 20)  # None은 기본 폰트
    small_font = pygame.font.Font(None, 16)

class ChatClient:
    def __init__(self, host='<Server IP>', port=5555):
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.nickname = ""
        self.messages = []
        self.input_text = ""
        self.connected = False
        self.users = []  # 접속 중인 사용자 목록
        
    def connect(self, nickname):
        try:
            self.client_socket.connect((self.host, self.port))
            self.nickname = nickname
            self.connected = True
            
            # 닉네임 전송
            receive_thread = threading.Thread(target=self.receive_messages)
            receive_thread.daemon = True
            receive_thread.start()
            return True
        except:
            return False
            
    def receive_messages(self):
        while self.connected:
            try:
                message = self.client_socket.recv(1024).decode('utf-8')
                if message == 'NICK':
                    self.client_socket.send(self.nickname.encode('utf-8'))
                elif message.startswith('USER_LIST:'):
                    # 사용자 목록 업데이트
                    try:
                        user_data = json.loads(message[10:])
                        if user_data["type"] == "user_list":
                            self.users = user_data["users"]
                    except:
                        pass
                else:
                    self.messages.append(message)
                    # 메시지가 너무 많으면 오래된 메시지 삭제
                    if len(self.messages) > 15:
                        self.messages.pop(0)
            except:
                self.connected = False
                self.client_socket.close()
                break
                
    def send_message(self, message):
        if message and self.connected:
            try:
                self.client_socket.send(message.encode('utf-8'))
                # 서버에서 메시지를 다시 보내주므로 여기서는 추가하지 않음
                return True
            except:
                return False
        return False
        
    def disconnect(self):
        self.connected = False
        self.client_socket.close()

def main():
    client = ChatClient()
    clock = pygame.time.Clock()
    
    # 로그인 상태 변수
    logged_in = False
    nickname_input = ""
    
    running = True
    while running:
        screen.fill(WHITE)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                if client.connected:
                    client.disconnect()
                    
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                    if client.connected:
                        client.disconnect()
                
                elif not logged_in:
                    if event.key == pygame.K_RETURN and nickname_input:
                        if client.connect(nickname_input):
                            logged_in = True
                        else:
                            print("서버 연결 실패")
                    elif event.key == pygame.K_BACKSPACE:
                        nickname_input = nickname_input[:-1]
                    else:
                        nickname_input += event.unicode
                else:  # 로그인 상태
                    if event.key == pygame.K_RETURN and client.input_text:
                        if client.send_message(client.input_text):
                            client.input_text = ""
                    elif event.key == pygame.K_BACKSPACE:
                        client.input_text = client.input_text[:-1]
                    else:
                        client.input_text += event.unicode
        
        # 로그인 화면 또는 채팅 화면 표시
        if not logged_in:
            # 로그인 화면
            login_text = font.render("닉네임을 입력하세요:", True, BLACK)
            screen.blit(login_text, (WIDTH//2 - login_text.get_width()//2, HEIGHT//2 - 50))
            
            pygame.draw.rect(screen, GRAY, (WIDTH//2 - 150, HEIGHT//2, 300, 40))
            nickname_surface = font.render(nickname_input, True, BLACK)
            screen.blit(nickname_surface, (WIDTH//2 - 145, HEIGHT//2 + 10))
            
            instruction = small_font.render("Enter 키를 눌러 접속하세요", True, BLACK)
            screen.blit(instruction, (WIDTH//2 - instruction.get_width()//2, HEIGHT//2 + 60))
        else:
            # 채팅 화면
            # 메시지 표시 영역
            pygame.draw.rect(screen, LIGHT_BLUE, (50, 50, WIDTH-250, HEIGHT-150))
            
            # 사용자 목록 영역
            pygame.draw.rect(screen, LIGHT_GREEN, (WIDTH-190, 50, 140, HEIGHT-150))
            
            # 사용자 목록 제목
            users_title = font.render("접속자 목록", True, BLACK)
            screen.blit(users_title, (WIDTH-180, 60))
            
            # 사용자 목록 표시
            user_y_offset = 90
            for user in client.users:
                user_surface = small_font.render(user, True, BLACK)
                screen.blit(user_surface, (WIDTH-180, user_y_offset))
                user_y_offset += 25
            
            # 메시지 표시
            y_offset = 70
            for msg in client.messages:
                msg_surface = font.render(msg, True, BLACK)
                screen.blit(msg_surface, (60, y_offset))
                y_offset += 30
                
            # 입력 영역
            pygame.draw.rect(screen, GRAY, (50, HEIGHT-80, WIDTH-100, 40))
            input_surface = font.render(client.input_text, True, BLACK)
            screen.blit(input_surface, (60, HEIGHT-70))
            
            # 상태 표시
            status = small_font.render(f"접속됨: {client.nickname}", True, BLACK)
            screen.blit(status, (50, 20))
            
            # 도움말
            help_text = small_font.render("메시지 입력 후 Enter 키를 누르세요. ESC 키로 종료", True, BLACK)
            screen.blit(help_text, (50, HEIGHT-30))
        
        pygame.display.flip()
        clock.tick(30)
        
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()