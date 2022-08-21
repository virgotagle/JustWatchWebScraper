"""Just Watch Web Scraper"""
import os
from dataclasses import dataclass
from requests import Session, session
from bs4 import BeautifulSoup
from dotenv import load_dotenv
load_dotenv()


@dataclass
class JustWatchData:
    """Just Watch Data"""
    title: str
    just_watch_full_path: str
    type: str
    imdb_score: float
    imdb_id: str
    streaming_source: str
    streaming_link: str
    poster_url: str
    youtube_link_ids: list[str]
    cast: list[list[str]]
    rating: str
    genres: str
    runtime: str
    director: str
    synopsis: str

    def __init__(self, data, html: str) -> None:
        self.title = data['node']['content']['title']
        self.just_watch_full_path = data['node']['content']['fullPath']
        self.type = data['node']['objectType']
        self.imdb_score = data['node']['content']['scoring']['imdbScore']
        self.streaming_source = data['node']['watchNowOffer']['package']['clearName']
        self.streaming_link = data['node']['watchNowOffer']['standardWebURL']
        self.poster_url = data['node']['content']['posterUrl']
        soup = BeautifulSoup(html, 'html.parser')
        self.get_youtube_link_ids(soup)
        self.get_imdb_id(soup)
        self.get_cast(soup)
        self.get_other_details(soup)
        self.get_synopsis(soup)

    def get_youtube_link_ids(self, soup: BeautifulSoup):
        """Get Show/Movie YouTube Link Ids from Details Page"""
        div_youtube_players = soup.select(
            "div[class='youtube-player__image-preview-container'] > img")
        self.youtube_link_ids = []
        if len(div_youtube_players):
            self.youtube_link_ids = [div_youtube_player.attrs["src"].split("/")[4]
                                     for div_youtube_player in div_youtube_players]

    def get_imdb_id(self, soup: BeautifulSoup):
        """Get Show/Movie IMDB Id from Details Page"""
        div = soup.find("div", attrs={"v-uib-tooltip": "IMDB"})
        self.imdb_id = ""
        if div:
            a_element = div.next
            if "href" in a_element.attrs:
                link: str = a_element.attrs["href"]
                if link:
                    self.imdb_id = link.split("/")[4]

    def get_cast(self, soup: BeautifulSoup):
        """Get Show/Movie List of Cast from Details Page"""
        results: list[list[str]] = []
        divs = soup.select("div[class='title-credits__actor']")
        for div in divs:
            a_element = div.find("a")
            strong_element = div.find("strong")
            if strong_element and a_element:
                results.append(
                    [a_element.next.strip(), strong_element.next.strip()])
        self.cast = results

    def get_other_details(self, soup: BeautifulSoup):
        """Get Show/Movie Other Details from Details Page"""
        results: dict = {}
        for element in soup.select("div[class='detail-infos']"):
            label_element = element.select_one(
                "div[class='detail-infos__subheading']")
            label = label_element.text
            if label and label not in results:
                details_element = element.select_one(
                    "div[class='detail-infos__value']")
                details = details_element.text.strip()
                results[label] = details
        self.rating = results['Rating'] if "Rating" in results else ""
        self.genres = results['Genres'] if "Genres" in results else ""
        self.runtime = results['Runtime'] if "Runtime" in results else ""
        self.director = results['Director'] if "Director" in results else ""
        return results

    def get_synopsis(self, soup: BeautifulSoup):
        """Get Show/Movie Synopsis from Details Page"""
        for element in soup.select("h2[class='detail-infos__subheading--label']"):
            if element.text == "Synopsis":
                prev_element = element.previous_element.previous_element
                synopsis_element = prev_element.find("span")
                self.synopsis = synopsis_element.text
                break


class JustWatch():
    """Just Watch Web Scraper"""
    session: Session = None
    popular_after_cursor: str = ""

    def __init__(self) -> None:
        self.session = session()

    def get_payload(self):
        """ Just Watch API Graphql Payload """
        return {
            "operationName": "GetPopularTitles",
            "variables": {
                "popularTitlesSortBy": "POPULAR",
                "first": 40,
                "platform": "WEB",
                "sortRandomSeed": 0,
                "popularAfterCursor": self.popular_after_cursor,
                "popularTitlesFilter": {
                    "ageCertifications": [],
                    "excludeGenres": [],
                    "excludeProductionCountries": [],
                    "genres": [],
                    "objectTypes": [],
                    "productionCountries": [],
                    "packages": [
                        os.getenv("PACKAGE")
                    ],
                    "excludeIrrelevantTitles": False,
                    "presentationTypes": [],
                    "monetizationTypes": []
                },
                "watchNowFilter": {
                    "packages": [
                        os.getenv("PACKAGE")
                    ],
                    "monetizationTypes": []
                },
                "language": "en",
                "country": os.getenv("COUNTRY")
            },
            "query": "query GetPopularTitles($country: Country!, $popularTitlesFilter: TitleFilter, $watchNowFilter: WatchNowOfferFilter!, $popularAfterCursor: String, $popularTitlesSortBy: PopularTitlesSorting! = POPULAR, $first: Int! = 40, $language: Language!, $platform: Platform! = WEB, $sortRandomSeed: Int! = 0, $profile: PosterProfile, $backdropProfile: BackdropProfile, $format: ImageFormat) {\n  popularTitles(\n    country: $country\n    filter: $popularTitlesFilter\n    after: $popularAfterCursor\n    sortBy: $popularTitlesSortBy\n    first: $first\n    sortRandomSeed: $sortRandomSeed\n  ) {\n    totalCount\n    pageInfo {\n      startCursor\n      endCursor\n      hasPreviousPage\n      hasNextPage\n      __typename\n    }\n    edges {\n      ...PopularTitleGraphql\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment PopularTitleGraphql on PopularTitlesEdge {\n  cursor\n  node {\n    id\n    objectId\n    objectType\n    content(country: $country, language: $language) {\n      title\n      fullPath\n      scoring {\n        imdbScore\n        __typename\n      }\n      posterUrl(profile: $profile, format: $format)\n      ... on ShowContent {\n        backdrops(profile: $backdropProfile, format: $format) {\n          backdropUrl\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    likelistEntry {\n      createdAt\n      __typename\n    }\n    dislikelistEntry {\n      createdAt\n      __typename\n    }\n    watchlistEntry {\n      createdAt\n      __typename\n    }\n    watchNowOffer(country: $country, platform: $platform, filter: $watchNowFilter) {\n      id\n      standardWebURL\n      package {\n        packageId\n        clearName\n        __typename\n      }\n      retailPrice(language: $language)\n      retailPriceValue\n      lastChangeRetailPriceValue\n      currency\n      presentationType\n      monetizationType\n      availableTo\n      __typename\n    }\n    ... on Movie {\n      seenlistEntry {\n        createdAt\n        __typename\n      }\n      __typename\n    }\n    ... on Show {\n      seenState(country: $country) {\n        seenEpisodeCount\n        progress\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n"
        }

    def get_shows(self):
        """Get data from Just Watch Graphql"""
        results = self.session.post(
            "https://apis.justwatch.com/graphql", json=self.get_payload())
        results_json = results.json()
        if len(results_json['data']['popularTitles']['edges']):
            last_data = results_json['data']['popularTitles']['edges'][-1]
            self.popular_after_cursor = last_data['cursor']
            return results_json['data']['popularTitles']['edges']
        return []

    def get_details(self, full_path: str):
        """Get Just Watch Details HTML Page"""
        if full_path:
            results = self.session.get(
                f"https://www.justwatch.com{full_path}")
            return results.text
        return None
