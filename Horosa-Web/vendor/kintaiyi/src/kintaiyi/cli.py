"""
kintaiyi CLI - 太乙神數命令列工具

Usage examples:
    kintaiyi calculate --year 2026 --month 3 --day 24 --hour 12 --minute 30 --mode year
    kintaiyi calculate --date 2026-03-24 --time 12:30 --mode day
    kintaiyi calculate --date 2026-03-24 --time 12:30 --mode life --sex male
"""

import json
from datetime import datetime
from enum import Enum

import typer

from . import __version__

app = typer.Typer(
    name="kintaiyi",
    help="太乙神數排盤工具 - Taiyi Shenshu Divination Calculator",
    add_completion=False,
)


class Mode(str, Enum):
    year = "year"
    month = "month"
    day = "day"
    hour = "hour"
    minute = "minute"
    life = "life"


class OutputFormat(str, Enum):
    text = "text"
    json = "json"
    markdown = "markdown"


# Mapping from CLI mode names to ji_style integers used by Taiyi
_MODE_TO_JI_STYLE: dict[str, int] = {
    "year": 0,
    "month": 1,
    "day": 2,
    "hour": 3,
    "minute": 4,
    "life": 5,
}


def _parse_date_time(
    date_str: str | None,
    time_str: str | None,
    year: int | None,
    month: int | None,
    day: int | None,
    hour: int | None,
    minute: int | None,
) -> tuple[int, int, int, int, int]:
    """Resolve date/time from either --date/--time or individual components."""
    if date_str is not None:
        try:
            d = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            raise typer.BadParameter(f"Invalid date format: '{date_str}'. Expected YYYY-MM-DD.") from None
        year = d.year
        month = d.month
        day = d.day

    if time_str is not None:
        try:
            t = datetime.strptime(time_str, "%H:%M")
        except ValueError:
            raise typer.BadParameter(f"Invalid time format: '{time_str}'. Expected HH:MM.") from None
        hour = t.hour
        minute = t.minute

    now = datetime.now()
    year = year if year is not None else now.year
    month = month if month is not None else now.month
    day = day if day is not None else now.day
    hour = hour if hour is not None else now.hour
    minute = minute if minute is not None else now.minute

    return year, month, day, hour, minute


def _format_text(result: dict) -> str:
    """Format a result dict as plain text."""
    lines: list[str] = []
    for key, value in result.items():
        lines.append(f"{key}: {value}")
    return "\n".join(lines)


def _format_json(result: dict) -> str:
    """Format a result dict as JSON."""
    return json.dumps(result, ensure_ascii=False, indent=2, default=str)


def _format_markdown(result: dict) -> str:
    """Format a result dict as Markdown table."""
    lines: list[str] = ["| 項目 | 內容 |", "| --- | --- |"]
    for key, value in result.items():
        lines.append(f"| {key} | {value} |")
    return "\n".join(lines)


_FORMATTERS = {
    "text": _format_text,
    "json": _format_json,
    "markdown": _format_markdown,
}


@app.command()
def calculate(
    year: int | None = typer.Option(None, "--year", "-y", help="Year (公元年)"),
    month: int | None = typer.Option(None, "--month", "-m", help="Month (月)"),
    day: int | None = typer.Option(None, "--day", "-d", help="Day (日)"),
    hour: int | None = typer.Option(None, "--hour", "-H", help="Hour (時, 0-23)"),
    minute: int | None = typer.Option(None, "--minute", "-M", help="Minute (分, 0-59)"),
    date: str | None = typer.Option(None, "--date", help="Date in YYYY-MM-DD format"),
    time: str | None = typer.Option(None, "--time", help="Time in HH:MM format"),
    mode: Mode = typer.Option(Mode.year, "--mode", help="Calculation mode (year/month/day/hour/minute/life)"),
    output: OutputFormat = typer.Option(OutputFormat.text, "--output", "-o", help="Output format (text/json/markdown)"),
    method: int = typer.Option(0, "--method", help="Taiyi method: 0=統宗, 1=金鏡, 2=淘金歌, 3=太乙局"),
    sex: str | None = typer.Option(None, "--sex", "-s", help="Sex for life mode: male(男) or female(女)"),
) -> None:
    """Calculate a Taiyi Shenshu (太乙神數) divination board."""
    from .kintaiyi import Taiyi

    y, m, d, h, mi = _parse_date_time(date, time, year, month, day, hour, minute)

    taiyi = Taiyi(y, m, d, h, mi)

    if mode.value == "life":
        sex_map = {"male": "男", "female": "女"}
        sex_val = sex_map.get(sex, sex) if sex else None
        if sex_val not in ("男", "女"):
            raise typer.BadParameter("Life mode requires --sex (male/男 or female/女).")
        result = taiyi.taiyi_life(sex_val)
    else:
        ji_style = _MODE_TO_JI_STYLE[mode.value]
        result = taiyi.pan(ji_style, method)

    formatter = _FORMATTERS[output.value]
    typer.echo(formatter(result))


@app.command()
def version() -> None:
    """Show the kintaiyi version."""
    typer.echo(f"kintaiyi {__version__}")


def main() -> None:
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
