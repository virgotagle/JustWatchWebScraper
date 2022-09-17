"""Just Watch Test"""
from bs4 import BeautifulSoup
from src.just_watch import JustWatch, JustWatchData


def test():
    """Test get data from Just Watch Graphql"""
    just_watch = JustWatch()
    just_watch_shows = just_watch.get_shows()
    assert len(just_watch_shows) > 0
    data = JustWatchData(
        just_watch_shows[0], just_watch.get_details(just_watch_shows[0]['node']['content']['fullPath']))
    assert data.director != ''
    assert data.title != ''
