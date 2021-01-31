from sqlalchemy import Column, ForeignKey, Integer, PrimaryKeyConstraint

from rfhub2.db.model.base_class import Base


class SuiteRel(Base):
    parent_id = Column(Integer, ForeignKey("suite.id", ondelete="CASCADE"))
    child_id = Column(Integer, ForeignKey("suite.id", ondelete="CASCADE"))
    degree = Column(Integer)

    __table_args__ = (PrimaryKeyConstraint(parent_id, child_id),)

    def __str__(self):  # pragma: no cover
        return f"SuiteRel({self.parent_id},{self.child_id},{self.degree})"

    def __repr__(self):  # pragma: no cover
        return str(self)
