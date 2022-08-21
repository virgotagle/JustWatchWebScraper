"""Just Watch Web Scraper Sample"""
import pandas as pd
from src.just_watch import JustWatch, JustWatchData


def save_to_csv(limit: int = 0):
    """Save to CSV"""
    just_watch = JustWatch()
    shows: list[any] | None = None
    results: list[JustWatchData] = []
    count: int = 0
    while shows is None or len(shows) == 40:
        shows = just_watch.get_shows()
        for show in shows:
            print(f"downloading {show['node']['content']['title']}..")
            data = JustWatchData(
                show, just_watch.get_details(show['node']['content']['fullPath']))
            results.append(data)
        count += 40
        if limit != 0 and count >= limit:
            break
    data_frame = pd.DataFrame(results)
    data_frame.to_csv("sample.csv", index=False)


if __name__ == "__main__":
    save_to_csv(100)
