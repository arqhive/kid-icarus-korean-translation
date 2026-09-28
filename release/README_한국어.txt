광신화 파르테나의 거울 (GBA) 한글 패치 v0.1
제작: arqhive / 2026-09-29

대상: 패미컴 미니 24 광신화 파르테나의 거울 일본판 (FPTJ)
원본 파일명 예:
Famicom Mini 24 - Hikari Shinwa - Palthena no Kagami (Japan).gba

[적용]
1. 본인이 소유한 게임에서 덤프한 일본판 원본을 준비합니다.
2. IPS 도구에서 원본과 Palthena_KO_v0.1.ips를 선택해 적용합니다.
   ROM 확장을 지원하는 도구가 필요합니다. 기존 한글판에 덧씌우지 마세요.
3. 결과가 8,388,608바이트인지 확인하고 아래 SHA-256을 비교합니다.
4. 에뮬레이터에서 새로 부팅합니다. 이전 버전 강제 저장 상태는 사용하지 마세요.

[Python으로 적용]
Python 3.11 이상이면 추가 패키지 없이 사용할 수 있습니다.
ZIP의 모든 파일을 같은 폴더에 푼 뒤 다음 명령을 실행합니다.

python apply_patch.py "Famicom Mini 24 - Hikari Shinwa - Palthena no Kagami (Japan).gba" "Palthena_KO_v0.1.gba"

원본·패치·결과의 SHA-256을 자동 검사합니다.
완성 ROM은 지정한 위치와 실제 Windows 바탕화면에 저장합니다.

[확인값]
원본 크기: 4,194,304바이트
원본 SHA-256: 7a2118c605713898a8befa0dce2835998481bcbdd92850379620450de6209e4b
결과 크기: 8,388,608바이트
결과 SHA-256: 415815acb85c53e1143e304c5bcec72e46fdf213cdf294fc43083f6acc9c78ba
기타 확인값: manifest.json

[내용과 제한]
한글 로고, 게임 메뉴·대사·엔딩, 공통 메뉴 등 47개 메시지 블록을 적용했습니다.
한글과 로고의 세로 흔들림을 수정했습니다.
원래 영문인 그래픽은 유지했습니다. 이름 입력은 영문·숫자만 지원합니다.
mGBA에서 새 부팅·L+R 메뉴·계속하기·처음부터 동작을 확인했습니다.
실제 기기와 전체 구간 플레이, 모든 통신·저장 오류 조건, 절전 해제는 미검증입니다.
기존 내부 개발판 v3과 ROM 내용은 같습니다. 공개 버전은 v0.1입니다.

[크레딧·라이선스]
자체 도구·한국어 번역 기여분·문서: MIT License (LICENSE)
갈무리 폰트: Lee Minseo (quiple), SIL OFL 1.1 (Galmuri-OFL.md)
Nintendo와 무관한 비공식 팬 번역입니다. 게임의 상표·저작권은 Nintendo에 있습니다.
원본 ROM과 패치된 ROM은 배포하지 마세요.
