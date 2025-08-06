# 풋살장 예약 알리미 (futsal-notifier)

'iamground.kr' 웹사이트에서 특정 조건에 맞는 풋살장 예약 정보를 스크래핑하여 사용자에게 보여주는 Flask 기반 웹 애플리케이션입니다.

## 주요 기능

- **풋살장 검색**: 날짜, 지역, 시간을 기준으로 예약 가능한 풋살장을 검색합니다.
- **사용자 지정 검색 반경**: 검색 지점으로부터 원하는 반경(예: 1km, 3km, 5km, 10km, 20km) 내의 풋살장만 검색하여 보여줍니다.
- **향상된 지역 검색**: 입력된 지역명과 일치하는 풋살장뿐만 아니라, 해당 지역의 중심으로부터 지정된 반경 이내의 지리적으로 가까운 풋살장도 함께 검색합니다.
- **유연한 시간 검색**: 특정 시간을 검색할 때, 정확히 일치하는 시간대와 사용자가 설정한 근방 시간대(예: ±15분, ±30분)를 구분하여 보여줍니다.
- **실내/야외 필터링**: 풋살장의 실내/야외 여부를 기준으로 검색 결과를 필터링할 수 있습니다.
- **추천 인원수 표시**: 각 풋살장의 추천 인원수를 함께 표시하여 사용자가 적합한 구장을 쉽게 찾을 수 있도록 돕습니다.
- **정확한 구장 이름 표시**: 시설 이름과 개별 구장 이름을 조합하여 "시설명 (구장명)" 형태로 명확하게 표시합니다.
- **실시간 정보 제공**: 'iamground.kr'의 최신 예약 정보를 직접 조회하여 보여줍니다.
- **간편한 웹 인터페이스**: 사용자가 쉽게 검색 조건을 입력하고 결과를 확인할 수 있는 웹 페이지를 제공합니다.

## 기술 스택

- **Backend**: Flask, requests, gunicorn
- **Frontend**: HTML, CSS, JavaScript
- **외부 API**: Kakao Local API, iamground.kr API
- **배포**: AWS Elastic Beanstalk, Docker, CloudFormation, S3

## 파일 구조

```
futsal-notifier/
├── app.py              # Flask 애플리케이션 로직
├── Dockerfile          # 애플리케이션 컨테이너화 설정
├── requirements.txt    # Python 의존성 파일
├── cloudformation.yml  # AWS 인프라 정의 (IaC)
├── templates/
│   └── index.html      # 메인 웹 페이지
└── README.md           # 프로젝트 설명 파일
```

## AWS 배포 방법 (CloudFormation 사용)

이 프로젝트는 AWS CloudFormation을 사용하여 필요한 모든 인프라를 자동으로 생성하고 배포합니다.

### 1단계: 사전 준비

1.  **AWS 계정** 및 **AWS CLI**를 준비합니다.
2.  **Docker**를 로컬 컴퓨터에 설치합니다.
3.  **Kakao Local API 키**를 발급받습니다. ([카카오 개발자](https://developers.kakao.com/)에서 발급)

### 2단계: 소스 코드 압축 및 S3 업로드

1.  배포할 소스 코드를 `.zip` 파일로 압축합니다. (단, `.git`, `venv` 등 불필요한 파일은 제외)
    ```bash
    # 예시 (Linux/macOS):
    zip -r futsal-notifier.zip app.py Dockerfile requirements.txt templates/
    ```

2.  AWS S3에 배포용 버킷을 생성합니다. 버킷 이름은 전 세계적으로 고유해야 합니다.
    -   **추천 버킷 이름 형식**: `[프로젝트명]-artifacts-[AWS계정ID]-[리전]`
    -   **예시**: `futsal-notifier-artifacts-123456789012-ap-northeast-2`

3.  생성한 S3 버킷에 `futsal-notifier.zip` 파일을 업로드합니다.

### 3단계: CloudFormation 스택 생성

1.  AWS Management Console에 로그인하여 **CloudFormation** 서비스로 이동합니다.
2.  **"스택 생성"** > **"새 리소스 사용(표준)"**을 선택합니다.
3.  **"템플릿 파일 업로드"**를 선택하고 `cloudformation.yml` 파일을 업로드합니다.
4.  **스택 이름**을 입력합니다. (예: `futsal-notifier-stack`)
5.  **파라미터** 섹션에 다음 값을 입력합니다.
    -   `KakaoApiKey`: 발급받은 카카오 API 키
    -   `SourceS3Bucket`: 2단계에서 생성한 S3 버킷 이름
    -   `SourceS3Key`: S3에 업로드한 `.zip` 파일 이름 (예: `futsal-notifier.zip`)
6.  나머지 옵션은 기본값으로 두고 스택 생성을 완료합니다.

### 4단계: 배포 확인

-   스택 생성이 완료되면 (약 5-10분 소요), CloudFormation 스택의 **"출력(Outputs)"** 탭으로 이동합니다.
-   `EBEnvironmentUrl`에 표시된 URL을 클릭하여 배포된 애플리케이션을 확인합니다.

## 로컬에서 실행 방법

1.  **가상 환경 생성 및 활성화**
2.  **의존성 설치**: `pip install -r requirements.txt`
3.  **Kakao API 키 설정**: `KAKAO_API_KEY` 환경 변수에 발급받은 카카오 API 키를 설정합니다.
    ```bash
    # Windows (명령 프롬프트)
    set KAKAO_API_KEY=YOUR_KAKAO_API_KEY
    # Windows (PowerShell)
    $env:KAKAO_API_KEY="YOUR_KAKAO_API_KEY"
    # Linux/macOS
    export KAKAO_API_KEY=YOUR_KAKAO_API_KEY
    ```
4.  **애플리케이션 실행**: `python app.py`
5.  웹 브라우저에서 `http://127.0.0.1:5000`으로 접속합니다.