from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
import requests
import os
from typing import Optional
from dotenv import load_dotenv
from urllib.parse import urlencode, quote

# .env 파일 로드
load_dotenv()

app = FastAPI()

# 환경 변수에서 API 키 가져오기
ODSAY_API_KEY = os.getenv("ODSAY_API_KEY")

# 필수 환경 변수 검증
if not ODSAY_API_KEY:
    raise ValueError("ODSAY_API_KEY 환경 변수가 설정되지 않았습니다.")

# ODSAY API URL (고정)
ODSAY_API_BASE_URL = "https://api.odsay.com/v1/api/searchPubTransPathT"


class TravelTimeResponse(BaseModel):
    """응답 모델"""
    total_time: int  # 총 소요시간 (분)


def fetch_total_time_bus_only(
    start_lat: float,
    start_lon: float,
    end_lat: float,
    end_lon: float,
    lang: int = 0
) -> int:
    """
    ODSAY API를 호출하여 도시내 이동, 버스만 사용할 때의 totalTime 반환
    
    Args:
        start_lat: 출발지 위도
        start_lon: 출발지 경도
        end_lat: 도착지 위도
        end_lon: 도착지 경도
        lang: 언어 선택 (기본값: 0=국문)
    
    Returns:
        총 소요시간 (분)
    """
    # 파라미터 순서: apiKey, lang, SX, SY, EX, EY
    params = {
        "apiKey": ODSAY_API_KEY,
        "lang": lang,
        "SX": start_lon,      # 출발지 X좌표 (경도)
        "SY": start_lat,      # 출발지 Y좌표 (위도)
        "EX": end_lon,        # 도착지 X좌표 (경도)
        "EY": end_lat,        # 도착지 Y좌표 (위도)
        "SearchType": 0,      # 도시내 이동 (0 = 도시내 검색)
        "SearchPathType": 2,  # 버스만 사용 (2 = 버스)
        "output": "json"
    }
    
    try:
        # 쿼리 문자열을 미리 구성 (특수문자 인코딩하여 정확히 한 번만)
        query_string = urlencode(params, quote_via=quote)
        url = f"{ODSAY_API_BASE_URL}?{query_string}"
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        print(f"DEBUG: 요청 URL: {response.url}")
        print(f"DEBUG: API 응답: {data}")
        
        # API 응답에 error 필드가 있는지 확인
        if "error" in data:
            error_msg = data.get("error", [{}])[0].get("message", "Unknown error")
            raise ValueError(f"API 에러: {error_msg}")
        
        # API 응답 구조 확인
        if "result" not in data:
            raise ValueError(f"API 응답에 'result' 필드가 없습니다: {data}")
        
        result = data["result"]
        
        # path 배열에서 첫 번째 경로의 info.totalTime 추출
        if "path" not in result or len(result["path"]) == 0:
            raise ValueError("경로 데이터를 찾을 수 없습니다")
        
        # 버스만 검색한 경우, path[0]이 버스 경로
        first_path = result["path"][0]
        
        if "info" not in first_path:
            raise ValueError("경로 정보(info)를 찾을 수 없습니다")
        
        total_time = first_path["info"]["totalTime"]
        
        return total_time
    
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"API 호출 실패: {str(e)}")
    except (KeyError, ValueError) as e:
        raise HTTPException(status_code=500, detail=f"응답 파싱 실패: {str(e)}")


@app.get("/travel-time", response_model=TravelTimeResponse)
async def get_travel_time(
    start_lat: float = Query(..., description="출발지 위도"),
    start_lon: float = Query(..., description="출발지 경도"),
    end_lat: float = Query(..., description="도착지 위도"),
    end_lon: float = Query(..., description="도착지 경도"),
    lang: Optional[int] = Query(0, description="언어 (0=국문, 1=영문, 2=일문, 3=중문간체, 4=중문번체, 5=베트남어)")
) -> TravelTimeResponse:
    """
    도시간 이동, 버스만 사용할 때의 총 소요시간 반환
    
    Query Parameters:
        - start_lat: 출발지 위도
        - start_lon: 출발지 경도
        - end_lat: 도착지 위도
        - end_lon: 도착지 경도
        - lang: 언어 (선택, 기본값: 0)
    """
    total_time = fetch_total_time_bus_only(
        start_lat=start_lat,
        start_lon=start_lon,
        end_lat=end_lat,
        end_lon=end_lon,
        lang=lang
    )
    
    return TravelTimeResponse(total_time=total_time)


@app.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
