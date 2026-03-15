import os
import sys

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(BASE_DIR, "numerology"))
sys.path.append(os.path.join(BASE_DIR, "meishiki"))

from datetime import datetime
from typing import Optional

import kanshi_data as kd
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from unsei import Unsei

import numerology
from meishiki import Meishiki

load_dotenv()

app = FastAPI(title="Fortune Telling API For Demonstration", version="1.0.0")

origins_str = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173")
origins = [origin.strip() for origin in origins_str.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- レスポンスモデル定義 ---


class PillarsResponse(BaseModel):
    year_stem: str
    year_branch: str
    year_hidden_stems: str
    year_twelve_fortune: str
    year_stem_transformation_star: str
    year_branch_transformation_star: str
    month_stem: str
    month_branch: str
    month_hidden_stems: str
    month_twelve_fortune: str
    month_stem_transformation_star: str
    month_branch_transformation_star: str
    day_stem: str
    day_branch: str
    day_hidden_stems: str
    day_twelve_fortune: str
    day_stem_transformation_star: str
    day_branch_transformation_star: str
    hour_stem: str
    hour_branch: str
    hour_hidden_stems: str
    hour_twelve_fortune: str
    hour_stem_transformation_star: str
    hour_branch_transformation_star: str


class NumerologyResponse(BaseModel):
    life_path_number: int
    past_number: int
    future_number: int


# --- バリデーションヘルパー関数 ---


def validate_date_params(
    y: Optional[int], m: Optional[int], d: Optional[int], h: Optional[int] = None
) -> dict:
    """
    年、月、日のパラメータを検証し、datetime オブジェクトを返す。
    h は任意。
    """
    if y is None or m is None or d is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Year (y), Month (m), and Day (d) are required parameters.",
        )

    try:
        # h が指定されている場合は検証
        if h is not None:
            if h < 0 or h > 23:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid hour: {h}. Hour must be between 0 and 23.",
                )
            date_obj = datetime(year=y, month=m, day=d, hour=h)
        else:
            date_obj = datetime(year=y, month=m, day=d)

        return {
            "year": y,
            "month": m,
            "day": d,
            "hour": h,
            "date_object": date_obj,
            "has_hour": h is not None,
        }
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid date: {y}-{m}-{d}. Please check the values.",
        )


# --- エンドポイント実装 ---


@app.get(
    "/pillars", response_model=PillarsResponse, summary="Get Four Pillars of Destiny"
)
async def get_pillars(
    y: int = Query(..., description="Year of birth"),
    m: int = Query(..., description="Month of birth"),
    d: int = Query(..., description="Day of birth"),
    h: Optional[int] = Query(None, description="Hour of birth (optional, 0-23)"),
    g: Optional[int] = Query(0, description="Gender of birth"),
):
    """
    四柱推命 (Four Pillars of Destiny) のデータを取得します。
    時間(h)は任意パラメータです。
    """
    validated = validate_date_params(y, m, d, h)

    t_flag = validated["has_hour"]
    if t_flag:
        birthday = datetime.strptime(
            f"{validated['year']}-{validated['month']}-{validated['day']} {validated['hour']}:00",
            "%Y-%m-%d %H:%M",
        )
    else:
        birthday = datetime.strptime(
            f"{validated['year']}-{validated['month']}-{validated['day']}", "%Y-%m-%d"
        )

    meishiki = Meishiki(birthday, t_flag, g)
    meishiki.build_meishiki()

    unsei = Unsei(meishiki)
    unsei.build_unsei()

    return {
        "year_stem": kd.kan[meishiki.meishiki["tenkan"][0]],
        "year_branch": kd.shi[meishiki.meishiki["chishi"][0]],
        "year_hidden_stems": kd.kan[meishiki.meishiki["zokan"][0]],
        "year_twelve_fortune": kd.twelve_fortune[
            meishiki.meishiki["twelve_fortune"][0]
        ],
        "year_stem_transformation_star": kd.tsuhen[meishiki.meishiki["tsuhen"][0]],
        "year_branch_transformation_star": kd.tsuhen[meishiki.meishiki["tsuhen"][4]],
        "month_stem": kd.kan[meishiki.meishiki["tenkan"][1]],
        "month_branch": kd.shi[meishiki.meishiki["chishi"][1]],
        "month_hidden_stems": kd.kan[meishiki.meishiki["zokan"][1]],
        "month_twelve_fortune": kd.twelve_fortune[
            meishiki.meishiki["twelve_fortune"][1]
        ],
        "month_stem_transformation_star": kd.tsuhen[meishiki.meishiki["tsuhen"][1]],
        "month_branch_transformation_star": kd.tsuhen[meishiki.meishiki["tsuhen"][5]],
        "day_stem": kd.kan[meishiki.meishiki["tenkan"][2]],
        "day_branch": kd.shi[meishiki.meishiki["chishi"][2]],
        "day_hidden_stems": kd.kan[meishiki.meishiki["zokan"][2]],
        "day_twelve_fortune": kd.twelve_fortune[meishiki.meishiki["twelve_fortune"][2]],
        "day_stem_transformation_star": "－",
        "day_branch_transformation_star": kd.tsuhen[meishiki.meishiki["tsuhen"][6]],
        "hour_stem": kd.kan[meishiki.meishiki["tenkan"][3]] if t_flag else "－",
        "hour_branch": kd.shi[meishiki.meishiki["chishi"][3]] if t_flag else "－",
        "hour_hidden_stems": kd.kan[meishiki.meishiki["zokan"][3]] if t_flag else "－",
        "hour_twelve_fortune": kd.twelve_fortune[meishiki.meishiki["twelve_fortune"][3]]
        if t_flag
        else "－",
        "hour_stem_transformation_star": kd.tsuhen[meishiki.meishiki["tsuhen"][3]]
        if t_flag
        else "－",
        "hour_branch_transformation_star": kd.tsuhen[meishiki.meishiki["tsuhen"][7]]
        if t_flag
        else "－",
    }


@app.get(
    "/numerology", response_model=NumerologyResponse, summary="Get Numerology Numbers"
)
async def get_numerology(
    y: int = Query(..., description="Year of birth"),
    m: int = Query(..., description="Month of birth"),
    d: int = Query(..., description="Day of birth"),
):
    validated = validate_date_params(y, m, d)

    return {
        "life_path_number": numerology.calculate_life_path(
            validated["year"], validated["month"], validated["day"]
        ),
        "past_number": numerology.calculate_past_number(validated["day"]),
        "future_number": numerology.calculate_future_number(
            validated["month"], validated["day"]
        ),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
