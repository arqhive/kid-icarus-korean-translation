패미컴 미니 광신화 파르테나의 거울 (GBA) 한글 패치 v1.0f
제작: arqhive / 2026-10-07

대상: 패미컴 미니 24 광신화 파르테나의 거울 일본판 (FPTJ)
원본 파일명 예:
Famicom Mini 24 - Hikari Shinwa - Palthena no Kagami (Japan).gba

[적용]
1. 본인이 소유한 게임에서 덤프한 일본판 원본을 준비합니다.
2. IPS 도구에서 원본과 FPTJ_KPatch_v1.0f.ips를 선택해 적용합니다.
3. 결과가 4,194,304바이트인지 확인하고 아래 SHA-256을 비교합니다.
4. 완성된 ROM을 실행합니다.

[Python으로 적용]
Python 3.11 이상이면 추가 패키지 없이 사용할 수 있습니다.
ZIP의 모든 파일을 같은 폴더에 푼 뒤 다음 명령을 실행합니다.

python apply_patch.py "Famicom Mini 24 - Hikari Shinwa - Palthena no Kagami (Japan).gba"

원본·패치·결과의 SHA-256을 자동 검사하고 Palthena_KO_v1.0f.gba를 만듭니다.
완성 ROM은 지정한 위치와 실제 Windows 바탕화면에 저장합니다.

[확인값]
원본 크기: 4,194,304바이트
원본 SHA-256: 7a2118c605713898a8befa0dce2835998481bcbdd92850379620450de6209e4b
결과 크기: 4,194,304바이트
결과 SHA-256: d002667786f96b7919ecc9f4a6f39da328729e29be9f111ac8ccfa6e6d5c5173
기타 확인값: manifest.json

[3DS open_agb_firm]
이 게임은 EEPROM 64k 세이브를 씁니다. 패치한 ROM은 해시가 달라 세이브 방식이
기본값으로 잡히고 "카트리지 오류"가 뜹니다.
Palthena_KO_v1.0f.ini를 SD 카드의 /3ds/open_agb_firm/saves/ 에 넣으세요.
ROM 파일명이 Palthena_KO_v1.0f.gba 여야 적용됩니다.
전에 생긴 같은 이름의 .sav 가 있으면 지운 뒤 실행하세요.

[내용과 제한]
한글 로고, 게임 메뉴·대사·엔딩, 공통 메뉴 등 47개 메시지 블록을 적용했습니다.
원래 영어인 문구(PUSH START BUTTON., BEST, NO., FIN 등)는 그대로 두었습니다.
점수 화면의 "총점 / 점수"는 한글이 두 줄 높이라 위아래가 엇갈려 보입니다.
요새의 "구간 / 보스"는 한 칸 높이의 작은 한글로 그렸습니다.
3DS open_agb_firm과 mGBA에서 처음부터 엔딩까지 플레이해 확인했습니다.

[크레딧·라이선스]
자체 도구·한국어 번역 기여분·문서: MIT License (LICENSE)
갈무리 폰트: Lee Minseo (quiple), SIL OFL 1.1 (Galmuri-OFL.md)
Nintendo와 무관한 비공식 팬 번역입니다. 게임의 상표·저작권은 Nintendo에 있습니다.
원본 ROM과 패치된 ROM은 배포하지 마세요.
