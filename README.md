# Pygame 실시간 채팅 프로그램

Python 3.13과 Pygame을 사용한 간단한 실시간 채팅 프로그램입니다.

## 설치 방법

1. 필요한 패키지 설치:
```
pip install -r requirements.txt
or
pip3 install -r requirements.txt
```

## 실행 방법

1. 먼저 서버를 실행합니다:
```
python chat_server.py
or
python3 chat_server.py
```

2. 그 다음 클라이언트를 실행합니다(여러 창에서 실행 가능):
```
python chat_client.py
or
python chat_client.py
```

## 사용 방법

1. 클라이언트를 실행하면 닉네임을 입력하는 화면이 나타납니다.
2. 닉네임을 입력하고 Enter 키를 누르면 채팅방에 입장합니다.
3. 메시지를 입력하고 Enter 키를 누르면 메시지가 전송됩니다.
4. ESC 키를 누르면 프로그램이 종료됩니다.

## 기능

- 여러 사용자 간의 실시간 채팅
- 사용자 입장/퇴장 알림
- 간단한 그래픽 사용자 인터페이스