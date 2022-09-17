from sqlalchemy import Boolean, Column, DECIMAL,  DateTime, ForeignKey,  String
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.orm.session import Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy import create_engine
from src.just_watch import JustWatch, JustWatchData

Base = declarative_base()
metadata = Base.metadata


class JustWatchShows(Base):
    """Shows Model"""
    __tablename__ = 'shows'
    id = Column(INTEGER(11), primary_key=True)
    director = Column(String(255))
    title = Column(String(255))
    just_watch_full_path = Column(String(255))
    type = Column(String(255))
    imdb_score = Column(DECIMAL(20, 4))
    imdb_id = Column(String(255))
    streaming_source = Column(String(255))
    streaming_link = Column(String(255))
    poster_url = Column(String(255))
    rating = Column(String(255))
    genres = Column(String(255))
    runtime = Column(String(255))
    synopsis = Column(String(9999))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class JustWatchShowYT(Base):
    """YouTube Id Model"""
    __tablename__ = 'youtube'
    id = Column(INTEGER(11), primary_key=True)
    show_id = Column(ForeignKey('shows.id', ondelete='SET NULL',
                     onupdate='CASCADE'), index=True)
    youtube_id = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    shows = relationship('JustWatchShows')


class JustWatchShowCast(Base):
    """Cast Model"""
    __tablename__ = 'cast'
    id = Column(INTEGER(11), primary_key=True)
    show_id = Column(ForeignKey('shows.id', ondelete='SET NULL',
                     onupdate='CASCADE'), index=True)
    name = Column(String(255))
    character_name = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    shows = relationship('JustWatchShows')


class Database:
    """Just Watch Database"""

    def __init__(self) -> None:
        self.engine = create_engine('sqlite:///just_watch.db')
        self.__Session = sessionmaker(bind=self.engine)
        self.session: Session = self.__Session()
        metadata.create_all(self.engine)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, traceback):
        self.session.close()

    def insert(self, data: JustWatchData):
        """Insert Just Watch Data"""
        show = JustWatchShows()
        show.director = data.director
        show.title = data.title
        show.just_watch_full_path = data.just_watch_full_path
        show.type = data.type
        show.imdb_score = data.imdb_score
        show.imdb_id = data.imdb_id
        show.streaming_source = data.streaming_source
        show.streaming_link = data.streaming_link
        show.poster_url = data.poster_url
        show.rating = data.rating
        show.genres = data.genres
        show.runtime = data.runtime
        show.synopsis = data.synopsis
        self.session.add(show)
        self.session.flush()

        for youtube_id in data.youtube_link_ids:
            youtube = JustWatchShowYT()
            youtube.show_id = show.id
            youtube.youtube_id = youtube_id
            self.session.add(youtube)

        for name, character_name in data.cast:
            cast = JustWatchShowCast()
            cast.show_id = show.id
            cast.name = name
            cast.character_name = character_name
            self.session.add(cast)
        self.session.commit()
