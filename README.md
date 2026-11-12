# Mercury Game Template — 2인 1조 Pygame 슈팅게임 프로젝트

Thonny와 Pygame으로 학생 2명이 한 팀이 되어 게임을 **직접 개발**하기 위한 공통 프로젝트 구조입니다. 완성된 게임 코드는 제공하지 않습니다.

- 게임 기준 해상도: 1280 × 720 (16:9), 테스트 창 권장: 960 × 540
- 목표: 60 FPS, 종스크롤, 상하좌우 자유 이동
- 입력: 키보드, 이후 SPIKE Prime 연동
- 개발 미션: 게임 창 → 플레이어 → 이동 → 발사 → 적 → 충돌 → 체력 → 적 이동 → 적 공격 → 스테이지 → 아이템 → 보스 → UI → 최종 완성

## 첫 다운로드

```bash
git clone https://github.com/qmercury/mercuryGameTemplete.git
cd mercuryGameTemplete/shooting_game
```

Thonny에서 `main.py`를 열고 학생들이 1단계부터 구현합니다. Python용 Pygame은 Thonny 패키지 관리에서 `pygame-ce`를 설치해 사용할 수 있습니다.

이미 복제한 프로젝트의 변경 사항은 저장소 폴더에서 `git pull`로 가져옵니다. 학생들의 미커밋 작업이 있으면 먼저 저장·커밋하고 충돌을 확인하세요.

## 디렉터리

```text
shooting_game/
├── main.py
├── assets/
│   ├── images/
│   │   ├── player/
│   │   ├── enemies/
│   │   ├── bullets/
│   │   └── backgrounds/
│   └── audio/
│       ├── sfx/
│       │   ├── shoot/
│       │   ├── enemy/
│       │   ├── hit/
│       │   ├── explosion/
│       │   ├── damage/
│       │   ├── item/
│       │   ├── ui/
│       │   └── stage/
│       └── bgm/
├── preview.html
├── SOUND_CATALOG.csv
└── SOUND_README.md
```

이미지 폴더는 현재 비어 있고 `.gitkeep`으로 관리합니다. 효과음은 8개 종류의 WAV 30개가 포함되어 있으며, `shooting_game/preview.html`을 브라우저에서 열어 들어볼 수 있습니다. BGM은 아직 없습니다.

효과음 합성 원본(관리자용): `tools/generate_sfx_pack.py`. 실행하려면 `numpy scipy soundfile`을 설치하세요. 일반 학생은 실행하지 않아도 됩니다.
