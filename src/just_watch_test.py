"""Just Watch Test"""
from bs4 import BeautifulSoup
from src.just_watch import JustWatch, JustWatchData


def test_get_data():
    """Test get data from Just Watch Graphql"""
    just_watch = JustWatch()
    just_watch_data = just_watch.get_data()
    assert len(just_watch_data) > 0


def test_details_page():
    """Test Just Watch details page"""
    just_watch = JustWatch()
    just_watch_data = just_watch.get_data()
    details_page = just_watch.get_details_page(
        just_watch_data[0]['node']['content']['fullPath'])
    soup = BeautifulSoup(details_page, 'html.parser')
    title_divs = soup.select("div[class='title-block']")
    assert len(title_divs) > 0
    title = title_divs[0].text
    assert just_watch_data[0]['node']['content']['title'] in title


def test_data():
    """Test data from Just Watch"""
    just_watch = JustWatch()
    just_watch_data_list = just_watch.get_data()
    details_page = just_watch.get_details_page(
        just_watch_data_list[0]['node']['content']['fullPath'])
    just_watch_data = JustWatchData(just_watch_data_list[0], details_page)
    assert just_watch_data_list[0]['node']['content']['title'] in just_watch_data.title
