from pathlib import Path
import numpy as np
from scipy.signal import butter, sosfilt
import soundfile as sf
import csv, html, zipfile, shutil

SR=44100
rng=np.random.default_rng(20261112)
root=Path(__file__).resolve().parents[1] / 'sound_pack'
if root.exists(): shutil.rmtree(root)
(root/'assets'/'audio'/'sfx').mkdir(parents=True)
(root/'assets'/'audio'/'bgm').mkdir(parents=True)
(root/'assets'/'audio'/'bgm'/'.gitkeep').write_text('',encoding='utf-8')
records=[]

def tt(d): return np.arange(round(d*SR),dtype=np.float64)/SR

def fade(x, attack=.005, release=.03):
    n=len(x); a=min(round(SR*attack),n); r=min(round(SR*release),n)
    e=np.ones(n)
    if a:e[:a]=np.sin(np.linspace(0,np.pi/2,a))**2
    if r:e[-r:]=np.cos(np.linspace(0,np.pi/2,r))**2
    return x*e

def sweep(d,f0,f1,decay=2.5,kind='sine',vibrato=0,phase=0):
    t=tt(d); u=t/d
    # f0 and f1 Hz (logarithmic sweep)
    f=np.exp(np.log(max(1,f0))+(np.log(max(1,f1))-np.log(max(1,f0)))*u)
    if vibrato: f *= (1+vibrato*np.sin(2*np.pi*22*t))
    p=2*np.pi*np.cumsum(f)/SR+phase
    if kind=='triangle': s=2/np.pi*np.arcsin(np.sin(p))
    elif kind=='square': s=np.tanh(3*np.sin(p))
    elif kind=='saw': s=2*((p/(2*np.pi))%1)-1
    else: s=np.sin(p)
    return fade(s*np.exp(-decay*u),.004,max(.012,min(.07,d*.24)))

def filtered_noise(d, low=0, high=0, decay=2.7):
    t=tt(d); z=rng.standard_normal(len(t))
    if low and high:
        sos=butter(3,[low,high],btype='bandpass',fs=SR,output='sos')
    elif low:
        sos=butter(3,low,btype='highpass',fs=SR,output='sos')
    elif high:
        sos=butter(3,high,btype='lowpass',fs=SR,output='sos')
    else: sos=None
    if sos is not None:z=sosfilt(sos,z)
    z=z/(np.max(np.abs(z))+1e-12)
    return fade(z*np.exp(-decay*t/d),.002,min(.14,d*.22))

def silence(d): return np.zeros(round(d*SR))

def put(base, sound, at):
    i=int(at*SR); n=min(len(sound),len(base)-i)
    if n>0:base[i:i+n]+=sound[:n]

def notes(freqs,note_d=.13,gap=.008,decay=3.1,kind='sine'):
    dur=len(freqs)*(note_d+gap)+.1
    y=silence(dur)
    for i,f in enumerate(freqs):
        wav=sweep(note_d,f,f*.993,decay=decay,kind=kind)
        put(y,wav,i*(note_d+gap))
    return y

def export(category,name,desc,y):
    y=np.asarray(y,dtype=np.float64)
    if not np.isfinite(y).all():raise ValueError(name)
    # peak normalize to -2 dBFS max, with a gentle soft saturation
    y=np.tanh(y*1.1)
    p=np.max(np.abs(y)) if len(y) else 1
    y=y*(0.79/max(1e-9,p))
    pth=root/'assets'/'audio'/'sfx'/category
    pth.mkdir(parents=True,exist_ok=True)
    rel=Path('assets')/'audio'/'sfx'/category/(name+'.wav')
    sf.write(root/rel,y,SR,subtype='PCM_16')
    records.append((category,name+'.wav',desc,str(rel).replace('\\','/'),round(len(y)/SR,2)))

# PLAYERS shots
export('shoot','shoot_laser_01','기본 직선 레이저 — 가볍고 짧은 발사음', 0.8*sweep(.19,1050,210,2.3)+.14*filtered_noise(.19,high=7000,decay=6))
export('shoot','shoot_laser_02','밝은 2중 레이저 — 높은 음의 발사음', .6*sweep(.22,1500,330,2.2)+.35*sweep(.22,900,280,2.8,kind='triangle'))
export('shoot','shoot_plasma_01','플라즈마 발사 — 부드러운 전자음', .8*sweep(.30,640,150,2.1,kind='triangle',vibrato=.045)+.15*filtered_noise(.30,low=1400,decay=4))
y=silence(.25)
put(y,.7*sweep(.11,350,1600,2.5),0)
put(y,.6*sweep(.13,1700,260,3),.10)
export('shoot','shoot_plasma_02','플라즈마 펄스 — 짧은 상승·하강음', y)
export('shoot','shoot_cannon_01','강한 캐논 — 낮은 타격감', 1.2*sweep(.37,330,48,2.4,kind='square')+.6*filtered_noise(.37,high=1600,decay=6))

# ENEMY shots
export('enemy','enemy_shot_01','적 일반탄 — 짧고 낮은 전자음', sweep(.24,420,120,2.7,kind='square'))
export('enemy','enemy_shot_02','적 추적탄 — 흔들리는 전자음', sweep(.31,550,270,1.8,vibrato=.08,kind='triangle'))
y=silence(.37)
for i in range(3):put(y,sweep(.11,760-60*i,225,2.6,kind='square'),i*.102)
export('enemy','enemy_shot_03','적 연속탄 — 3연타',y)

# HITS
export('hit','hit_light_01','가벼운 명중 — 짧은 팅 소리', .5*sweep(.14,1500,730,4)+.8*filtered_noise(.14,low=1100,decay=7))
export('hit','hit_metal_01','금속 명중 — 날카로운 충돌음', .9*sweep(.25,1260,430,2,kind='triangle')+.6*sweep(.25,1810,540,3)+.4*filtered_noise(.25,low=850,decay=7))
export('hit','hit_shield_01','보호막 피격 — 울림 있는 소리', .9*sweep(.44,570,350,2,kind='sine',vibrato=.03)+.4*sweep(.44,1140,725,2.8))

# EXPLOSIONS
export('explosion','explosion_small_01','작은 폭발 — 일반 적 격추', 1.3*filtered_noise(.38,high=3800,decay=3)+.7*sweep(.38,155,45,2.4,kind='square'))
y=1.4*filtered_noise(.68,high=5400,decay=2)+.8*sweep(.68,210,38,2,kind='square')
for t in (.0,.08,.17):put(y,filtered_noise(.13,low=1200,decay=6)*.3,t)
export('explosion','explosion_medium_01','중간 폭발 — 강한 적 격추',y)
y=1.8*filtered_noise(1.05,high=4000,decay=1.7)+1.2*sweep(1.05,160,25,2.4,kind='square')
for t in (0,.13,.27,.48):put(y,filtered_noise(.22,high=9000,decay=4)*.5,t)
export('explosion','explosion_large_01','큰 폭발 — 다중 충격과 잔향',y)
y=1.4*filtered_noise(1.62,high=3700,decay=1.5)+1.5*sweep(1.62,180,28,2,kind='square')
for t in (0,.10,.24,.41,.69,.98):put(y,filtered_noise(.36,high=7500,decay=4)*.5,t)
export('explosion','explosion_boss_01','보스 폭발 — 긴 연속 폭발',y)

# PLAYER DAMAGE
export('damage','damage_alert_01','플레이어 피격 — 경고음', .65*sweep(.37,880,390,1.7,kind='square')+.4*filtered_noise(.37,high=1900,decay=4))
y=silence(.55)
for i in range(2):put(y,sweep(.19,510,510,1.2,kind='triangle'),i*.25)
export('damage','damage_alert_02','플레이어 피격 — 두 번 울리는 경고',y)

# ITEMS
export('item','item_powerup_01','무기 강화 — 4음 상승', notes([440,554.37,659.25,880],.12,.006,2.1))
y=notes([523,659,784,1047,1319],.10,.014,2.7)
y+=.18*sweep(len(y)/SR,990,1450,1.8)
export('item','item_powerup_02','무기 강화 — 반짝이는 높은 멜로디', y)
export('item','item_health_01','체력 회복 — 부드러운 3음', notes([392,523,659],.19,.025,2.6))
export('item','item_coin_01','아이템 획득 — 짧은 2음',notes([740,1110],.11,.014,3.2))

# UI
export('ui','ui_select_01','메뉴 선택 — 짧은 클릭음',sweep(.10,850,1100,4,kind='triangle'))
export('ui','ui_select_02','메뉴 선택 — 낮은 클릭음',sweep(.095,460,610,4,kind='triangle'))
export('ui','ui_start_01','게임 시작 — 상승 멜로디',notes([392,494,587,784],.15,.035,1.9))
export('ui','ui_pause_01','일시정지 — 짧은 하강음',sweep(.22,690,280,2.2,kind='triangle'))
export('ui','ui_gameover_01','게임 오버 — 하강 멜로디',notes([660,550,440,330],.24,.03,1.8,kind='triangle'))
export('ui','ui_clear_01','게임 클리어 — 승리 멜로디',notes([523,659,784,1047,988,1175,1319],.16,.022,1.8))

# STAGE
export('stage','stage_transition_01','스테이지 전환 — 상승 효과', .8*sweep(.75,230,1200,1.6,kind='triangle')+.28*filtered_noise(.75,high=6500,decay=3))
y=silence(1.1)
for i in range(3):put(y,sweep(.25,440,410,1.7,kind='square'),i*.33)
export('stage','stage_warning_01','보스 경고 — 반복 경보',y)
y=notes([220,277,330,440,550],.23,.045,1.8,kind='triangle')
put(y,filtered_noise(.38,high=6000,decay=3)*.23,0)
export('stage','stage_boss_intro_01','보스 등장 — 긴 긴장감 효과',y)

# README & CSV
with (root/'SOUND_CATALOG.csv').open('w',encoding='utf-8-sig',newline='') as fp:
    w=csv.writer(fp)
    w.writerow(['category','filename','description_ko','relative_path','seconds'])
    w.writerows(records)

intro='''# Pygame 종스크롤 슈팅게임 — 선택형 효과음 라이브러리\n\n2인 1조 학생팀이 취향에 맞게 효과음을 골라 쓰도록 만든 교육용 샘플입니다.\n모두 외부 음원 샘플 없이 파형 합성 방식으로 새로 제작한 44.1kHz / 16-bit / 모노 WAV 파일입니다.\n\n## 시작하기\n\n1. 압축을 풀고 `preview.html`을 브라우저로 열어 효과음을 듣습니다.\n2. 원하는 효과음을 선택해 게임의 `assets/audio/sfx/` 폴더에서 사용합니다.\n3. 팀 기록지에 선택한 파일명을 기록합니다.\n4. `assets/audio/bgm/` 폴더는 추후 배경음악을 추가할 공간입니다. 배경음악은 포함되어 있지 않습니다.\n\n## 폴더와 효과음 용도\n\n- `shoot/`: 플레이어 총알 발사\n- `enemy/`: 적 총알 발사\n- `hit/`: 총알이 목표물에 맞음\n- `explosion/`: 적 또는 보스의 폭발\n- `damage/`: 플레이어 피격\n- `item/`: 무기 강화·체력 회복·아이템 획득\n- `ui/`: 메뉴 선택·게임 시작·일시정지·게임 오버·클리어\n- `stage/`: 스테이지 전환·보스 경고·보스 등장\n\n## 수업 운영 권장 사항\n\n- 2인 1조가 공통 효과음 파일 중 서로 다른 것을 골라도 됩니다.\n- 먼저 `shoot`, `hit`, `explosion`의 소리를 선택해 기본 게임에 적용합니다.\n- 학생들이 효과음이 재생되어야 하는 상황(이벤트)을 직접 설계하도록 합니다.\n- 연속 발사 소리는 지나치게 길거나 큰 소리를 선택하지 않도록 합니다.\n- BGM과 효과음은 각각 볼륨을 조절할 수 있도록 게임에서 분리하는 것을 권장합니다.\n- 학습용 기본 합성음이라 전문 스튜디오 제작 음원과 질감이 다를 수 있습니다.\n\n## 저작권 및 이용\n\n이 팩의 WAV 파일은 이번 프로젝트를 위해 새로 합성한 음원입니다.\n학생 수업·학습용 게임에 자유롭게 사용하거나 수정·공유할 수 있습니다.\n제3자 음원은 포함되어 있지 않습니다.\n\n파일 목록과 길이는 `SOUND_CATALOG.csv`를 참고하세요.\n'''
(root/'README.md').write_text(intro,encoding='utf-8')

styles='''<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Pygame 슈팅게임 효과음 미리듣기</title><style>body{font-family:system-ui,-apple-system,"Apple SD Gothic Neo",sans-serif;max-width:920px;margin:24px auto;padding:0 18px;color:#1c2d43;background:#fafcfe}h1{font-size:24px}p{color:#536174}h2{margin-top:30px;color:#34516f}table{width:100%;border-collapse:collapse;background:#fff;border-radius:12px;overflow:hidden}td,th{text-align:left;padding:11px;border-bottom:1px solid #e8edf5;font-size:13px}th{background:#edf5fc}audio{width:200px;height:35px}code{font-size:12px;color:#31526e}@media(max-width:600px){td,th{padding:6px;font-size:12px}audio{width:126px}code{word-break:break-word}}</style></head><body><h1>🎮 슈팅게임 효과음 라이브러리</h1><p>각 효과음을 들어보고 팀 게임에 어울리는 소리를 골라보세요. 파일은 모두 WAV이며, 목록에서 파일명을 확인할 수 있습니다.</p>'''
labels={'shoot':'플레이어 발사','enemy':'적 발사','hit':'명중','explosion':'폭발','damage':'플레이어 피격','item':'아이템','ui':'게임 메뉴·결과','stage':'스테이지·보스'}
for cat,label in labels.items():
    styles+=f'<h2>{label}</h2><table><tr><th>파일</th><th>효과음 설명</th><th>미리듣기</th></tr>'
    for c,name,desc,path,dur in records:
        if c!=cat: continue
        styles+=f'<tr><td><code>{html.escape(name)}</code></td><td>{html.escape(desc)}</td><td><audio controls preload="none" src="{html.escape(path,quote=True)}"></audio></td></tr>'
    styles+='</table>'
styles+='''<p>이 HTML 파일을 압축 해제한 폴더에서 열어야 상대 경로의 WAV 파일을 재생할 수 있습니다.</p></body></html>'''
(root/'preview.html').write_text(styles,encoding='utf-8')
zipname=root.parent / 'pygame_shooter_sound_pack.zip'
with zipfile.ZipFile(zipname,'w',zipfile.ZIP_DEFLATED,compresslevel=8) as zp:
    for file in root.rglob('*'):
        if file.is_file():zp.write(file,arcname=str(Path(root.name)/file.relative_to(root)))
print('Count:',len(records),'Total duration:',round(sum(r[-1] for r in records),1),'seconds')
print('Zip:',zipname, 'bytes',zipname.stat().st_size)
print('Category counts:',{c:sum(r[0]==c for r in records) for c in labels})
print('Preview exists:',(root/'preview.html').exists())
print('WAV sample:',sf.info(root/'assets/audio/sfx/shoot/shoot_laser_01.wav'))