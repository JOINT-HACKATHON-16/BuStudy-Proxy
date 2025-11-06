from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import os
from typing import Optional
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

app = FastAPI()

# 환경 변수에서 API 키와 URL 가져오기
ODSAY_API_KEY = os.getenv("ODSAY_API_KEY")
ODSAY_API_URL = os.getenv("ODSAY_API_URL")

# 필수 환경 변수 검증
if not ODSAY_API_KEY:
    raise ValueError("ODSAY_API_KEY 환경 변수가 설정되지 않았습니다.")
if not ODSAY_API_URL:
    raise ValueError("ODSAY_API_URL 환경 변수가 설정되지 않았습니다.")


class LocationRequest(BaseModel):
    """위치 요청 모델"""
    start_lat: float  # 출발지 위도 (Y좌표)
    start_lon: float  # 출발지 경도 (X좌표)
    end_lat: float    # 도착지 위도 (Y좌표)
    end_lon: float    # 도착지 경도 (X좌표)
    lang: Optional[int] = 0  # 언어 (기본값: 국문)


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
    ODSAY API를 호출하여 도시간 이동, 버스만 사용할 때의 totalTime 반환
    
    Args:
        start_lat: 출발지 위도
        start_lon: 출발지 경도
        end_lat: 도착지 위도
        end_lon: 도착지 경도
        lang: 언어 선택 (기본값: 0=국문)
    
    Returns:
        총 소요시간 (분)
    """
    params = {
        "apiKey": ODSAY_API_KEY,
        "SX": start_lon,      # 출발지 X좌표 (경도)
        "SY": start_lat,      # 출발지 Y좌표 (위도)
        "EX": end_lon,        # 도착지 X좌표 (경도)
        "EY": end_lat,        # 도착지 Y좌표 (위도)
        "SearchType": 1,      # 도시간 이동 (1 = 도시간 이동/도시내 이동 구분검색)
        "SearchPathType": 2,  # 버스만 사용 (2 = 버스)
        "lang": lang,
        "output": "json"
    }
    
    try:
        response = requests.get(ODSAY_API_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # API 응답 구조 확인
        if "result" not in data:
            raise ValueError(f"API 응답에 'result' 필드가 없습니다: {data}")
        
        result = data["result"]
        
        # path 배열에서 첫 번째 경로의 info.totalTime 추출
        if "path" not in result or len(result["path"]) == 0:
            raise ValueError("경로 데이터를 찾을 수 없습니다")
        
        # 첫 번째 경로 선택
        first_path = result["path"][0]
        
        if "info" not in first_path:
            raise ValueError("경로 정보(info)를 찾을 수 없습니다")
        
        total_time = first_path["info"]["totalTime"]
        
        return total_time
    
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"API 호출 실패: {str(e)}")
    except (KeyError, ValueError) as e:
        raise HTTPException(status_code=500, detail=f"응답 파싱 실패: {str(e)}")


@app.post("/travel-time", response_model=TravelTimeResponse)
async def get_travel_time(request: LocationRequest) -> TravelTimeResponse:
    """
    도시간 이동, 버스만 사용할 때의 총 소요시간 반환
    
    Args:
        request: 출발지/도착지 좌표 정보
    
    Returns:
        TravelTimeResponse: 총 소요시간 (분)
    """
    total_time = fetch_total_time_bus_only(
        start_lat=request.start_lat,
        start_lon=request.start_lon,
        end_lat=request.end_lat,
        end_lon=request.end_lon,
        lang=request.lang
    )
    
    return TravelTimeResponse(total_time=total_time)


@app.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
