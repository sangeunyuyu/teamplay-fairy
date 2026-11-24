# ✦ Jet Send Star | 초고속 무로그인 우주 파일 전송

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.40+-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![SQLite3](https://img.shields.io/badge/SQLite3-Embedded-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)

<br/>

**"USB도, 이메일 로그인도 필요 없는 1회용 무로그인 보안 파일 전송 서비스"**  
공공장소 PC나 발표장 스크린에서 계정 유출 걱정 없이 **4자리 코드** 또는 **QR 코드**로 즉시 다운로드하세요.

[🚀 데모 실행하기](#-빠른-시작-quick-start) • [✨ 핵심 기능](#-핵심-기능-key-features) • [🛠️ 기술 스택](#-기술-스택-tech-stack) • [📖 사용 가이드](#-사용-방법-how-to-use)

</div>

---

## 🌌 프로젝트 개요 (Overview)

세미나 발표, 강의실, 또는 회의실 공용 PC에서 발표 자료(PPT, PDF, 영상 등)를 열기 위해 **개인 이메일이나 카카오톡, 클라우드에 로그인한 뒤 로그아웃을 잊어버린 경험**이 있으신가요? 또는 공용 PC의 악성코드나 바이러스 걱정 때문에 USB를 꽂기 망설여진 적이 있으신가요?

**Jet Send Star**는 이러한 마찰(Friction)과 보안 위협을 완벽히 해결하기 위해 개발된 **무로그인 휘발성(Ephemeral) 파일 전송 웹 애플리케이션**입니다.

- **로그인 제로**: 계정 생성, 로그인, 개인정보 수집이 전혀 없습니다.
- **간편한 전송**: 누구나 쉽게 외우고 입력할 수 있는 **4자리 숫자 코드**와 모바일 스캔용 **QR 코드**를 제공합니다.
- **강력한 보안**: 지정된 시간(5~60분) 경과 시 자동 파기되며, **1회 다운로드 즉시 영구 파기(Burn-after-download)** 기능을 지원합니다.
- **감각적인 디자인**: Apple 스타일의 세련된 글래스모피즘(Glassmorphism)과 반응형 우주(Cosmic) 테마 애니메이션을 적용했습니다.

---

## ✨ 핵심 기능 (Key Features)

### 1. 🚀 초간편 4자리 전송 코드 발급
- 파일을 드래그앤드롭하고 발사 버튼을 누르면 **4자리 숫자 코드**가 즉시 발급됩니다.
- 수신자 PC에서 4자리 번호만 입력하면 즉시 다운로드가 시작됩니다.

### 2. 📱 발표 PC & 모바일 즉시 연동 QR 코드
- 로컬/네트워크 IP를 자동으로 감지하여 **다이렉트 다운로드 링크** 및 **고해상도 QR 코드**를 실시간 렌더링합니다.
- 스마트폰 카메라 또는 발표 컴퓨터 웹캠으로 스캔하면 해당 파일의 수신 페이지로 즉시 연결됩니다 (`?code=XXXX` 쿼리 파라미터 지원).

### 3. 🔥 강력한 휘발성 보안 (Auto-Destruct & Burn Mode)
- **유효 시간 선택**: 5분(초단기 보안), 10분(발표 권장), 30분(강의용), 60분(장시간 회의)
- **1회 다운로드 즉시 파기**: 수신자가 다운로드를 완료하는 순간 데이터베이스에서 파일이 영구 삭제되어 흔적을 남기지 않습니다.
- **백그라운드 자동 정리**: 만료 시간이 지난 파일은 다음 작업 시 자동 삭제 처리됩니다.

### 4. 🎨 Apple-Grade Cosmic Glassmorphism UI
- 심우주(Deep Space) 그라디언트 캔버스, 성운(Nebula) 블러 효과, 별똥별(Shooting Star) 애니메이션
- 파일 확장자별 스마트 아이콘 및 메타 정보 시각화 (PPT, PDF, Word, 압축파일, 미디어 등)
- 중앙 정렬 대형 PIN 코드 입력 인터페이스

---

## 🛠️ 기술 스택 (Tech Stack)

| 영역 | 기술 | 설명 |
| :--- | :--- | :--- |
| **Frontend & App Framework** | `Streamlit` | 빠르고 반응성이 뛰어난 인터랙티브 Python 웹 프레임워크 |
| **Styling & Animation** | `Custom CSS / HTML5` | 글래스모피즘, 키프레임 애니메이션, SF Pro 및 JetBrains Mono 폰트 |
| **Database** | `SQLite3` (Embedded) | 별도 DB 서버 설정 없이 바이너리(BLOB)와 메타데이터를 저장하는 내장형 DB |
| **Utility & Media** | `qrcode[pil]`, `Pillow` | 다운로드 다이렉트 URL 인코딩 및 이미지 버퍼 기반 실시간 QR 생성 |
| **Networking** | `socket` (Python Standard) | 로컬 네트워크 IP 자동 감지를 통한 LAN 내 크로스 디바이스 전송 지원 |

---

## 🚀 빠른 시작 (Quick Start)

### 1. 저장소 클론 (Clone Repository)
```bash
git clone https://github.com/your-username/jet-send-star.git
cd jet-send-star
```

### 2. 가상환경 생성 및 패키지 설치 (Install Dependencies)
```bash
# 가상환경 생성 (선택 사항)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 필수 패키지 설치
pip install -r requirements.txt
```

### 3. 앱 실행 (Run Application)
```bash
streamlit run app.py
```
실행 후 브라우저가 자동으로 열리거나 `http://localhost:8501`로 접속할 수 있습니다.

---

## 📖 사용 방법 (How to Use)

### 📤 파일 보내기 (Sender)
1. 상단 탭에서 **`🚀 파일 보내기 (Send)`**를 선택합니다.
2. 전송할 파일을 드래그하여 업로드합니다.
3. 원하는 **유효 보관 시간**(5분~1시간)과 **1회 다운로드 즉시 파기** 옵션을 선택합니다.
4. **`✦ 우주로 초고속 발사`** 버튼을 클릭합니다.
5. 화면에 표시되는 **4자리 코드**를 발표자에게 알려주거나, 화면의 **QR 코드 / 다이렉트 링크**를 제공합니다.

### 📥 파일 받기 (Receiver)
1. 수신 PC에서 앱에 접속한 후 **`📥 파일 받기 (Receive)`** 탭을 선택합니다.  
   *(QR 코드나 다이렉트 링크로 접속한 경우 코드가 자동으로 입력됩니다.)*
2. 전달받은 **4자리 숫자 코드**를 입력합니다.
3. 파일 정보와 남은 시간을 확인하고 **`⬇️ 다운로드 시작`** 버튼을 클릭합니다.
4. 1회 다운로드 파기 옵션이 켜져 있는 파일은 다운로드 완료 즉시 서버에서 영구 소멸됩니다.

---

## 🌐 전세계 배포 방법 (Deployment)

### Streamlit Community Cloud (무료 1-클릭 배포)
1. 본 프로젝트를 본인의 GitHub 저장소에 푸시(Push)합니다.
2. [share.streamlit.io](https://share.streamlit.io)에 접속하여 GitHub 계정으로 로그인합니다.
3. **`New app`** 클릭 후 해당 저장소와 브랜치를 선택하고 메인 파일 경로를 `app.py`로 지정합니다.
4. **`Deploy!`**를 누르면 수 분 내에 전 세계 누구나 접속할 수 있는 퍼블릭 URL이 생성됩니다.

---

## 🔮 향후 개발 로드맵 (Future Roadmap)

- [ ] **E2EE(종단간 암호화)**: Web Crypto API 기반 클라이언트 사이드 비밀번호 암/복호화 적용
- [ ] **대용량 파일 분할 청크 전송**: 메모리 사용량을 최소화하는 스트리밍 디스크 스토리지 분리
- [ ] **WebRTC P2P 직결 모드**: 서버를 거치지 않는 브라우저 간 초고속 다이렉트 데이터 전송
- [ ] **다운로드 알림 푸시**: 수신자가 파일을 받았을 때 발신자 화면에 실시간 완료 알림 팝업

---

## 📄 라이선스 (License)

This project is licensed under the MIT License - see the LICENSE file for details.

---

<div align="center">
  <sub>Crafted with passion for Frictionless Presentations & Secure Transfers.</sub>
</div>
