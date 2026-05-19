# PyInstaller + Pygame 이미지 및 사운드 적용 정리

## 1. 목적

Pygame 게임에서:

- 이미지 로드
- 사운드 재생
- 배경음 재생
- PyInstaller로 exe 변환 후에도 정상 실행

이 가능하도록 설정함.

---

# 2. PyInstaller용 resource_path 함수

## 수정 전 문제 코드

```python
def resource_path(relative_path("Graphics")):
```

문법 오류가 발생함.

---

## 수정 후 정상 코드

```python
import sys
import os

def resource_path(relative_path):
    """개발 중과 빌드 후 모두 동작하는 경로 반환"""

    if hasattr(sys, '_MEIPASS'):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(__file__)

    return os.path.join(base, relative_path)
```

---

# 3. 경로 추가 방법

## 잘못된 방식

```python
def resource_path(relative_path("Graphics")):
```

함수 안에 경로를 넣는 것이 아님.

---

## 올바른 방식

```python
resource_path("Graphics/abyss_snake_assets/Graphics/apple.png")
```

이미지나 사운드를 로드할 때 경로를 넣어야 함.

---

# 4. 이미지 로드

## 사과 이미지

```python
apple_img = pygame.image.load(
    resource_path("Graphics/abyss_snake_assets/Graphics/apple.png")
)
```

---

## 뱀 머리 이미지

```python
head_img = pygame.image.load(
    resource_path("Graphics/abyss_snake_assets/Graphics/head_up.png")
)
```

---

# 5. 사운드 로드

## 먹는 소리

```python
eat_sound = pygame.mixer.Sound(
    resource_path("Graphics/snake_sound_pack/eat.wav")
)
```

---

## 죽는 소리

```python
die_sound = pygame.mixer.Sound(
    resource_path("Graphics/snake_sound_pack/die.wav")
)
```

---

## 배경음

```python
pygame.mixer.music.load(
    resource_path("Graphics/snake_sound_pack/bgm.wav")
)
```

---

# 6. 폴더 구조

```plaintext
프로젝트
│
├── main.py
│
└── Graphics
    ├── abyss_snake_assets
    │   └── Graphics
    │       ├── apple.png
    │       ├── head_up.png
    │       └── ...
    │
    └── snake_sound_pack
        ├── bgm.wav
        ├── eat.wav
        └── die.wav
```

---

# 7. PyInstaller 설치

```bash
pip install pyinstaller
```

---

# 8. exe 파일 만들기

## Windows

```bash
pyinstaller --onefile --add-data "Graphics;Graphics" main.py
```

---

## Mac/Linux

```bash
pyinstaller --onefile --add-data "Graphics:Graphics" main.py
```

---

# 9. 옵션 설명

| 옵션 | 설명 |
|---|---|
| --onefile | exe 하나로 압축 |
| --add-data | 이미지/사운드 포함 |
| Graphics;Graphics | Graphics 폴더 전체 추가 |

---

# 10. exe 위치

빌드 완료 후:

```plaintext
dist/main.exe
```

에서 실행 가능.

---

# 11. 결과

정상적으로:

- 이미지 출력
- 사운드 재생
- 배경음 반복 재생
- 다른 컴퓨터에서도 실행 가능

상태가 됨.

---

# 12. 추가로 가능한 기능

추가로:

- exe 아이콘 적용
- 콘솔창 제거
- 용량 최적화
- 로딩 화면 추가
- 자동 전체화면
- 애니메이션 최적화

등을 적용 가능.