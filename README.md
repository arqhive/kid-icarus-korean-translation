# 패미컴 미니 광신화 파르테나의 거울 (GBA) 한글 패치

*ファミコンミニ24 光神話 パルテナの鏡* (게임보이 어드밴스, 일본판 `FPTJ`) 비공식 한국어 팬 패치입니다.
대사는 일본어판 원문을 기준으로 번역했습니다.

**제작: arqhive** · **최신 버전: [v1.0f](https://github.com/arqhive/kid-icarus-korean-translation/releases/tag/v1.0f)** (최종판)

- 타이틀 로고를 원작 분위기에 맞춘 **광신화 파르테나의 거울** 로고로 바꿨습니다.
- 이름 등록·기록 삭제·상태·점수·게임 오버·엔딩 문구와 신전·상점·병원 등의 대사 14개를 한글화했습니다.
- 패미컴 미니 공통 메뉴, 저장·삭제·오류·절전·통신 안내 등 일본어 메시지 블록 47개를 한글화했습니다.
- 갈무리7·갈무리11 폰트를 사용했습니다. 요새의 "구간 / 보스" 표시줄은 원본처럼 위아래로 맞추려고 한 칸 높이의 작은 한글을 따로 그렸습니다.
- 원래 영어인 문구(`PUSH START BUTTON.`, `BEST`, `NO.`, `FIN` 등)는 그대로 두었습니다.
- ROM 크기는 원본과 같은 4 MiB입니다. 배포본은 원본에 적용하는 **IPS 패치**입니다.

> Git 관리 대상에는 **게임 ROM, 게임에서 추출한 원문 대사·그래픽·스크린샷이 들어 있지 않습니다.**
> 패치를 만들거나 적용하려면 본인이 소유한 게임에서 직접 덤프한 원본이 필요합니다.

## 사용자용: 패치 적용

### 준비물

- 수정하지 않은 일본판 `Famicom Mini 24 - Hikari Shinwa - Palthena no Kagami (Japan).gba` (4,194,304바이트).
- IPS를 적용할 수 있는 패처. 동봉한 `apply_patch.py`를 쓰려면 Python 3.11 이상이 필요합니다.

| 항목 | 원본 일본판 | 패치 적용 결과 (v1.0f) |
|---|---|---|
| 크기 | 4,194,304 바이트 | 4,194,304 바이트 |
| CRC32 | `F311EDAC` | `BF3DF949` |
| MD5 | `76759e14e1a4072397c105419d702735` | `282b3a193b53732fb10a43d2914212bc` |
| SHA-1 | `cca6eb41ea8edc8115994fad2a0b329af44bb659` | `32cd1c2b131fa39e62623515dcae05c1399719ec` |
| SHA-256 | `7a2118c605713898a8befa0dce2835998481bcbdd92850379620450de6209e4b` | `d002667786f96b7919ecc9f4a6f39da328729e29be9f111ac8ccfa6e6d5c5173` |

### 적용 방법

[릴리즈 페이지](https://github.com/arqhive/kid-icarus-korean-translation/releases/tag/v1.0f)에서 `FPTJ_KPatch_v1.0f.zip`을 받습니다. 아래 개발자용 빌드 절차로 직접 만들 수도 있습니다.

1. ZIP을 폴더째 풉니다.
2. 일반 IPS 패처에서 `FPTJ_KPatch_v1.0f.ips`와 일본판 **원본** ROM을 선택하고 별도 결과 파일을 만듭니다. 또는 압축을 푼 폴더에서 아래 명령을 실행합니다.
3. 만들어진 `Palthena_KO_v1.0f.gba`를 실행합니다.

```powershell
python apply_patch.py "Famicom Mini 24 - Hikari Shinwa - Palthena no Kagami (Japan).gba"
```

동봉 패처는 원본·패치·결과의 SHA-256을 확인하고 원본을 보존합니다. 결과 파일 이름을 바꾸려면 원본 다음에 결과 경로를 붙입니다.
자세한 방법은 [`README_한국어.txt`](release/README_한국어.txt)를 참고하세요.

### 실행 환경

- **확인함**: 3DS open_agb_firm, Windows의 mGBA에서 처음부터 엔딩까지 플레이.

### 3DS open_agb_firm에서 쓸 때

이 게임은 EEPROM 64k 세이브를 씁니다. open_agb_firm은 세이브 방식을 ROM 해시로 찾는데, 패치한 ROM은 해시가 달라 기본값(EEPROM 8k)으로 잡히고 "카트리지 오류"가 뜹니다.
ZIP에 들어 있는 `Palthena_KO_v1.0f.ini`를 SD 카드의 `/3ds/open_agb_firm/saves/`에 넣으세요. ROM 파일명이 `Palthena_KO_v1.0f.gba`여야 적용됩니다.
전에 생긴 같은 이름의 `.sav`가 있으면 지운 뒤 실행하세요.

### 알려진 문제

- 점수 화면의 "총점 / 점수"는 위아래 글자가 엇갈려 보입니다. 원본은 한 줄 높이의 가나를 바로 위아래 줄에 붙여 썼는데, 한글 한 글자는 화면 타일 두 줄을 차지해서 위 단어의 아래 절반이 다음 줄까지 내려옵니다. 그래서 두 단어의 가로 위치를 어긋나게 두었고, 아래 단어는 반 줄 아래로 보입니다. 숫자는 원래 위치 그대로입니다.
- 요새의 "구간 / 보스" 표시줄은 한 칸 높이의 작은 한글이라 다른 글자보다 작습니다.

## 개발자용: 직접 빌드

### 요구 사항

- Python 3.12 이상. 검증 환경은 Python 3.13, numpy 2.5.3, Pillow 12.3.0입니다.
- `python -m pip install -r requirements.txt`로 빌드 의존성을 설치합니다.
- 일본판 원본 ROM을 `rom/`에 위 파일명으로 두거나 환경 변수 `PALTHENA_JP_ROM`으로 지정합니다.
- 갈무리 BDF 폰트와 한국어 로고 소스는 저장소에 포함되어 있습니다.
- 선택 사항: 실행 검증에는 64비트 Windows용 mGBA libretro DLL이 필요합니다. `vendor/mgba_libretro.dll`에 두거나 `MGBA_LIBRETRO`로 경로를 지정합니다. 빌드·패치 적용에는 필요하지 않습니다.

### 빌드

```powershell
# 원본에서 로고, 게임 텍스트, 공통 메뉴를 순서대로 빌드
python tools/build.py

# 선택 사항: 공통 메시지 정적 검증 및 mGBA 실행 회귀 검사
python tools/verify_text_v3.py

# 빌드 결과로 IPS·확인값·배포 ZIP 생성, 패치 적용 결과 검증
python tools/make_patch.py
```

완성 ROM은 `work/build/final/Palthena_KO_v1.0f.gba`에 생성됩니다.
최종 ROM 한 개만 실제 바탕화면에 같은 파일명으로 복사하고 해시를 확인합니다. 중간 단계 ROM은 `work/build/` 안에만 남습니다.
배포 파일은 `release/FPTJ_KPatch_v1.0f.zip`과 `release/FPTJ_KPatch_v1.0f.ips`입니다. ZIP은 Git에서 제외하며 명령으로 재생성합니다.

기존 작업 기록 없이 원본 ROM부터 빌드할 수 있습니다. 같은 입력·도구 버전에서는 같은 바이트가 생성됩니다.
검증용 `assert`를 사용하므로 `python -O`나 `PYTHONOPTIMIZE`를 사용하지 마세요.

### 번역 수정

- 게임 메뉴·대사: [`translation/game_ko.py`](translation/game_ko.py).
- GBA 공통 메뉴: [`translation/wrapper_ko.py`](translation/wrapper_ko.py). `(x, y, 문자열)`로 표시 위치를 지정합니다.
- 제목 로고: `tools/assets/title_logo_ko.png`, 부제·타이틀 배치: `tools/build_logo_v2.py`.
- 요새 표시줄의 작은 한글: `tools/build_text_patch.py`의 `SMALL`.
- 표기 원칙과 입력 제한: [`translation/GLOSSARY.md`](translation/GLOSSARY.md).

번역 파일에는 한국어와 표시용 영문·기호만 들어 있습니다. 일본어 원문과 비교 자료는 빌드 중 `work/build/static_kana_audit/`에 생성하며 커밋하지 않습니다.
번역을 고친 뒤 전체 빌드와 검증을 다시 실행하세요. 문자 수·글리프 뱅크·창 크기·대사 칸·NES 코드 공간 제한을 넘으면 빌드가 중단됩니다.
공개 버전은 `VERSION`을 기준으로 합니다. 도구 이름의 `v2`, `v3`는 내부 개발 단계 이름입니다.

### 폴더 구조

```text
tools/             빌드·패치·정적 조사·실행 검증 도구
  assets/          새로 제작한 한국어 타이틀 로고 소스
translation/       한국어 번역문과 표기 원칙
fonts/             갈무리7·갈무리11 BDF, SIL OFL 라이선스
docs/
  TECHNICAL.md     파일 구조와 한글화 방식
  releases/        릴리즈 노트 사본
release/           사용자 설명서·확인값 (생성된 IPS·ZIP·ini 포함)
rom/               (git 제외) 원본 ROM
vendor/            (git 제외) 선택적 mGBA libretro DLL
work/              (git 제외) 빌드 결과·추출 자료·미리보기
  legacy/          구조 정리 이전의 작업 기록
VERSION            공개 버전
```

### 기술 문서

파일 구조와 한글화 방식은 [`docs/TECHNICAL.md`](docs/TECHNICAL.md)에 정리했습니다.

## 변경 내역

전체 내역은 [`CHANGELOG.md`](CHANGELOG.md)에 있습니다.

## 크레딧·라이선스

- 이 저장소의 도구 코드, 한국어 번역 기여분, 문서: [MIT License](LICENSE) (© 2026 arqhive).
- 갈무리7·갈무리11: Lee Minseo (quiple), [SIL Open Font License 1.1](fonts/Galmuri-OFL.md). 폰트에는 MIT 라이선스가 적용되지 않습니다.
- 한국어 타이틀 로고: 원본의 분위기를 참고해 ImageGen으로 제작한 워드마크. 게임에서 추출한 타이틀 이미지는 포함하지 않았습니다.

## 면책

비공식 팬 번역이며 Nintendo와 관련이 없습니다. 「광신화 파르테나의 거울」 관련 상표·저작권은 Nintendo에 있습니다.
패치를 적용한 게임 파일의 배포를 금지합니다.
