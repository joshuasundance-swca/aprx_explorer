from __future__ import annotations

import json
import typing
import zipfile
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import pandas as pd
from pydantic import BaseModel, ConfigDict, model_validator

from aprx_explorer.tick_converter import TickConverter


class GPHistory(BaseModel):
    model_config = ConfigDict(extra="allow")

    start_time: datetime | None = None
    end_time: datetime | None = None
    run_duration: timedelta | None = None
    name: str | None = None
    text: str | None = None
    type: str | None = None
    iD: str | None = None
    catalogPath: str | None = None
    itemType: str | None = None
    propertiesXML: str | None = None
    sourceModifiedTime: dict[str, str] | None = None

    @model_validator(mode="before")
    def add_time_data(cls, values: dict) -> dict:  # type: ignore
        xml_str = values["propertiesXML"]
        xml_soup = BeautifulSoup(xml_str, "xml")
        start_ticks = xml_soup.find("process").get("ticks")
        end_ticks = xml_soup.find("process").get("ticks2")
        parsed_time = TickConverter.parse_start_end(start_ticks, end_ticks)
        return {
            **values,
            **dict(zip(("start_time", "end_time", "run_duration"), parsed_time)),
        }

    @classmethod
    def history_from_aprx(cls, aprx: str) -> typing.Iterable[GPHistory]:
        """Extracts geoprocessing history objects from an ArcGIS Pro project file."""
        # an aprx is a zipfile
        with zipfile.ZipFile(aprx) as zipfile_obj:
            # geoprocessing history is stored in this file
            with zipfile_obj.open("GISProject.json") as file_obj:
                json_str = file_obj.read()
                json_dict = json.loads(json_str)
        project_items = json_dict["projectItems"]
        history_objects = (
            item for item in project_items if item.get("itemType") == "GPHistory"
        )
        return (cls.model_validate(d) for d in history_objects)

    @classmethod
    def history_to_df(cls, history: typing.Iterable[GPHistory]) -> pd.DataFrame:
        starting_cols = [
            "start_time",
            "end_time",
            "name",
            "run_duration",
            "text",
            "iD",
            "catalogPath",
            "propertiesXML",
            "type",
            "itemType",
            "sourceModifiedTime",
        ]

        df = pd.DataFrame(
            h.model_dump(exclude_unset=True, exclude_defaults=True, exclude_none=True)
            for h in history
        )

        print(df)

        cols_in_df = [c for c in starting_cols if c in df.columns]
        other_cols = sorted(c for c in df.columns if c not in starting_cols)
        cols = cols_in_df + other_cols

        df = (
            df[cols]
            .sort_values("end_time")
            .reset_index(drop=True)
            .dropna(axis=1, how="all")
        )

        return df
