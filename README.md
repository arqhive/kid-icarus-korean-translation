# 광신화 파르테나의 거울 (GBA) 한글 패치

*ファミコンミニ24 光神話 パルテナの鏡* (게임보이 어드밴스, 일본판 `FPTJ`) 비공식 한국어 팬 패치입니다.
대사는 일본어판 원문을 기준으로 번역했습니다.

**제작: arqhive** · **최신 버전: [v0.1](docs/releases/v0.1.md)**

- 타이틀 로고를 원작 분위기에 맞춘 **광신화 파르테나의 거울** 로고로 바꿨습니다.
- 이름 등록·기록 삭제·상태·구간·점수·게임 오버·엔딩 문구와 상점·신전 등의 대사 14개를 한글화했습니다.
- 패미컴 미니 공통 메뉴, 저장·삭제·오류·절전·통신 안내 등 일본어 메시지 블록 47개를 한글화했습니다.
- 갈무리7·갈무리11 폰트를 사용했습니다. 게임 안 한글과 로고의 세로 흔들림을 수정했습니다.
- ROM 크기는 원본과 같은 4 MiB를 유지합니다. 배포물은 원본에 적용하는 IPS 패치입니다.

> Git 관리 대상에는 **게임 ROM, 게임에서 추출한 원문 대사·그래픽·스크린샷이 들어 있지 않습니다.**
> 패치를 만들거나 적용하려면 본인이 소유한 게임에서 직접 덤프한 원본이 필요합니다.

## 사용자용: 패치 적용

### 준비물

- 일본판 원본 GBA ROM. 아래 SHA-256과 일치해야 합니다.
- IPS 패치 도구 또는 Python 3.11 이상.
- 로컬 배포 폴더의 `Palthena_KO_v0.1_Patch.zip` 또는 [`Palthena_KO_v0.1.ips`](release/Palthena_KO_v0.1.ips).

### 적용 방법

1. `release/Palthena_KO_v0.1_Patch.zip`을 풉니다. 현재는 로컬 배포물이며 온라인 릴리즈는 게시하지 않았습니다.
2. 일본판 **원본** ROM에 `Palthena_KO_v0.1.ips`를 적용합니다. 이전 한글판에 덧씌우지 마세요.
3. 결과 파일의 확인값을 아래 표와 비교하고 GBA 에뮬레이터에서 새로 부팅합니다.

ZIP에 포함된 Python 도구는 원본·패치·결과의 SHA-256을 자동으로 검사합니다. 압축을 푼 폴더에서 실행하세요.

```powershell
python apply_patch.py "Famicom Mini 24 - Hikari Shinwa - Palthena no Kagami (Japan).gba" "Palthena_KO_v0.1.gba"
```

결과 ROM은 지정한 위치에 저장하고 실제 Windows 바탕화면에도 복사합니다.
자세한 방법은 [`README_한국어.txt`](release/README_한국어.txt)를 참고하세요.

### 파일 확인값

| 항목 | 원본 일본판 | 패치 적용 결과 (v0.1) |
|---|---|---|
| 크기 | 4,194,304 바이트 | 4,194,304 바이트 |
| CRC32 | `F311EDAC` | `58A2AE6A` |
| MD5 | `76759e14e1a4072397c105419d702735` | `6313243111c473210de5e499d3875d99` |
| SHA-1 | `cca6eb41ea8edc8115994fad2a0b329af44bb659` | `4d5d38522c42c218465b8314f283b6bba7505f15` |
| SHA-256 | `7a2118c605713898a8befa0dce2835998481bcbdd92850379620450de6209e4b` | `10f42479314b43db3325657a6d552530cce74a5e86bb8408d55e11abc3906d0c` |

원본 파일명 예: `Famicom Mini 24 - Hikari Shinwa - Palthena no Kagami (Japan).gba`

### 실행 환경

- **확인함**: 3DS open_agb_firm, Windows의 mGBA. 새 부팅, 이름 등록, 정지 화면, 게임 오버, 저장, L+R 메뉴 동작을 확인했습니다.
- 공통 메시지 47개는 ROM에서 글자·좌표를 읽어 정적으로 검증했습니다. 메뉴 글자 영역은 120프레임 동안 픽셀 변화가 없었습니다.
- **미확인**: 상점·신전 대사, 구간 클리어 점수 화면, 엔딩의 실제 표시, 모든 통신·저장 오류 조건, 절전 모드 해제.

### 3DS open_agb_firm에서 쓸 때

이 게임은 EEPROM 64k 세이브를 씁니다. open_agb_firm은 세이브 방식을 ROM 해시로 찾는데, 패치한 ROM은 해시가 달라 기본값(EEPROM 8k)으로 잡히고 "카트리지 오류"가 뜹니다.
ZIP에 들어 있는 `Palthena_KO_v0.1.ini`를 SD 카드의 `/3ds/open_agb_firm/saves/`에 넣으세요. ROM 파일명이 `Palthena_KO_v0.1.gba`여야 적용됩니다.
전에 생긴 `Palthena_KO_v0.1.sav`가 있으면 지운 뒤 실행하세요.

### 알려진 문제

- 원래 영문인 그래픽(`BEST`, `NO.`, `FIN` 등)은 유지했습니다.
- 이름 입력은 영문·숫자를 사용합니다. 한글 이름 입력은 지원하지 않습니다.
- 기존 버전의 에뮬레이터 강제 저장 상태를 불러오면 예전 글꼴·코드가 복원될 수 있습니다. ROM을 새로 부팅하세요.
- 공통 라이브러리의 통신 메시지는 이 게임에서 실제로 사용되지 않는 항목도 포함할 수 있습니다.
- 파일 수준에서 확인한 일본어 표시 경로를 번역했습니다. 모든 숨겨진 실행 경로를 플레이로 확인한 것은 아닙니다.

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

완성 ROM은 `work/build/final/Palthena_KO_v0.1.gba`에 생성됩니다.
최종 ROM 한 개만 실제 바탕화면에 같은 파일명으로 복사하고 해시를 확인합니다. 중간 단계 ROM은 `work/build/` 안에만 남습니다.
최종 배포 ZIP은 `release/Palthena_KO_v0.1_Patch.zip`입니다. ZIP은 Git에서 제외하며 명령으로 재생성합니다.

기존 작업 기록 없이 원본 ROM부터 빌드할 수 있습니다. 같은 입력·도구 버전에서는 같은 바이트가 생성됩니다.
검증용 `assert`를 사용하므로 `python -O`나 `PYTHONOPTIMIZE`를 사용하지 마세요.

### 번역 수정

- 게임 메뉴·대사: [`translation/game_ko.py`](translation/game_ko.py).
- GBA 공통 메뉴: [`translation/wrapper_ko.py`](translation/wrapper_ko.py). `(x, y, 문자열)`로 표시 위치를 지정합니다.
- 제목 로고: `tools/assets/title_logo_ko.png`, 부제·타이틀 배치: `tools/build_logo_v2.py`.
- 표기 원칙과 입력 제한: [`translation/GLOSSARY.md`](translation/GLOSSARY.md).

번역 파일에는 한국어와 표시용 영문·기호만 들어 있습니다. 일본어 원문과 비교 자료는 빌드 중 `work/build/static_kana_audit/`에 생성하며 커밋하지 않습니다.
번역을 고친 뒤 전체 빌드와 검증을 다시 실행하세요. 문자 수·글리프 뱅크·창 크기 제한을 넘으면 빌드가 중단됩니다.
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
release/           IPS 패치·사용자 설명서·확인값, 생성된 ZIP
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
