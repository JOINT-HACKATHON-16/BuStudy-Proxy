# BuStudy Proxy - ODSAY API 버스 경로 조회 서버

ODSAY API를 사용하여 도시간 버스 이동의 총 소요시간만 반환하는 FastAPI 서버입니다.

## 설치

### 1. 패키지 설치

```bash
pip install -r requirements.txt
```

### 2. 환경 변수 설정

ODSAY API 키를 환경 변수로 설정합니다:

```bash
export ODSAY_API_KEY="your-api-key-here"
```

또는 `.env` 파일을 생성하여 설정할 수 있습니다:

```bash
ODSAY_API_KEY=your-api-key-here
```

## 실행

```bash
python main.py
```

또는 uvicorn으로 직접 실행:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

서버는 `http://localhost:8000`에서 실행됩니다.

## API 엔드포인트

### 1. 소요시간 조회

**엔드포인트:** `POST /travel-time`

**요청 본문:**

```json
{
  "start_lat": 37.6134436427887,
  "start_lon": 126.926493082645,
  "end_lat": 37.5004198786564,
  "end_lon": 127.126936754911,
  "lang": 0
}
```

**요청 파라미터:**

- `start_lat` (float, 필수): 출발지 위도 (Y좌표)
- `start_lon` (float, 필수): 출발지 경도 (X좌표)
- `end_lat` (float, 필수): 도착지 위도 (Y좌표)
- `end_lon` (float, 필수): 도착지 경도 (X좌표)
- `lang` (int, 선택): 언어 선택 (기본값: 0)
  - 0: 국문
  - 1: 영문
  - 2: 일문
  - 3: 중문(간체)
  - 4: 중문(번체)
  - 5: 베트남어

**응답:**

```json
{
  "total_time": 45
}
```

### 2. 헬스 체크

**엔드포인트:** `GET /health`

**응답:**

```json
{
  "status": "ok"
}
```

## 사용 예시

### cURL

```bash
curl -X POST "http://localhost:8000/travel-time" \
  -H "Content-Type: application/json" \
  -d '{
    "start_lat": 37.6134436427887,
    "start_lon": 126.926493082645,
    "end_lat": 37.5004198786564,
    "end_lon": 127.126936754911
  }'
```

### Python

```python
import requests

url = "http://localhost:8000/travel-time"
payload = {
    "start_lat": 37.6134436427887,
    "start_lon": 126.926493082645,
    "end_lat": 37.5004198786564,
    "end_lon": 127.126936754911
}

response = requests.post(url, json=payload)
print(response.json())  # {"total_time": 45}
```

### JavaScript

```javascript
const response = await fetch("http://localhost:8000/travel-time", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    start_lat: 37.6134436427887,
    start_lon: 126.926493082645,
    end_lat: 37.5004198786564,
    end_lon: 127.126936754911,
  }),
});

const data = await response.json();
console.log(data); // { total_time: 45 }
```

## 주요 특징

- ✅ ODSAY API 자동 호출
- ✅ 도시간 이동 (InterCity) 지원
- ✅ 버스만 사용하는 경로 필터링
- ✅ 총 소요시간만 단순하게 반환
- ✅ 다국어 지원
- ✅ 에러 처리 및 상세한 에러 메시지
- ✅ FastAPI 자동 문서화 (Swagger UI)

## API 문서

서버 실행 후 다음 URL에서 Swagger UI를 통해 API를 테스트할 수 있습니다:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## 트러블슈팅

### 1. "API 호출 실패" 에러

- ODSAY_API_KEY 환경 변수가 올바르게 설정되었는지 확인하세요
- API 키의 유효성을 확인하세요

### 2. "경로 데이터를 찾을 수 없습니다" 에러

- 주어진 좌표 간에 버스 경로가 없을 수 있습니다
- 좌표값이 올바른지 확인하세요

### 3. "응답 파싱 실패" 에러

- ODSAY API 응답 형식이 변경되었을 수 있습니다
- API 문서를 다시 확인하세요

## 라이선스

MIT
