from sqlalchemy import Column, Integer, Sequence, Text, Time

from rfhub2.db.model.base_class import Base


class Statistics(Base):
    id = Column(Integer, Sequence("statistics_id_seq"), primary_key=True)
    collection = Column(Text, index=True)
    keyword = Column(Text, index=True)
    times_used = Column(Integer)
    total_elapsed_time = Column(Time)

    def __str__(self):  # pragma: no cover
        return f"Statistics({self.id},{self.collection},{self.keyword},{self.times_used},{self.total_elapsed_time})"

    def __repr__(self):  # pragma: no cover
        return str(self)
