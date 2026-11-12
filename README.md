# Pygame 2D Shooter — 2인 1조 프로젝트 템플릿

학생들이 Thonny와 Pygame으로 직접 개발하는 종스크롤 슈팅게임 수업의 공통 에셋 저장소입니다.

- 기준 해상도: 1280×720 (16:9)
- 테스트 창: 960×540
- 목표 FPS: 60
- 조작: 키보드 → 추후 SPIKE Prime 컨트롤러 연동
- 개발 방식: 2인 1조, 총 14단계 미션
- 완성된 게임 코드는 포함하지 않습니다. 학생들이 직접 구현합니다.

## 효과음 라이브러리

`sound_pack/`에 8개 분류, 30개 WAV 효과음, 미리듣기 페이지와 목록이 있습니다.
`sound_pack/preview.html`을 다운로드한 폴더에서 열면 소리를 들어볼 수 있습니다.

재생성 방법:

```bash
python -m pip install numpy scipy soundfile
python tools/generate_sfx_pack.py
```

Pygame 프로젝트에 사용할 때는 `sound_pack/assets/audio/sfx/`를 게임의 `assets/audio/sfx/`에 복사하세요.

## 구성

```text
README.md
tools/generate_sfx_pack.py
sound_pack/
  README.md
  SOUND_CATALOG.csv
  preview.html
  assets/audio/sfx/
    shoot/ enemy/ hit/ explosion/ damage/ item/ ui/ stage/
  assets/audio/bgm/
```

> 기본 효과음은 직접 파형 합성으로 제작한 교육용 소리입니다. 자유롭게 사용·수정·공유할 수 있습니다.
