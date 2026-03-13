from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional, Type, TypeVar, Generic

T = TypeVar('T')

class CodeRepository(Generic[T]):
    def __init__(self, db: Session = None):
        self.db = db
    
    def set_db(self, db: Session):
        self.db = db
    
    def save(self, entity: T) -> T:
        """保存实体"""
        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)
        return entity
    
    def update(self, entity: T) -> T:
        """更新实体"""
        self.db.commit()
        self.db.refresh(entity)
        return entity
    
    def delete(self, entity: T):
        """删除实体"""
        self.db.delete(entity)
        self.db.commit()
    
    def find_by_id(self, model: Type[T], id: int) -> Optional[T]:
        """根据ID查找实体"""
        return self.db.query(model).filter_by(id=id).first()
    
    def find_by_criteria(self, model: Type[T], **kwargs) -> List[T]:
        """根据条件查找实体"""
        return self.db.query(model).filter_by(**kwargs).all()
    
    def find_all(self, model: Type[T], order_by=None, limit: int = None) -> List[T]:
        """查找所有实体"""
        query = self.db.query(model)
        if order_by is not None:
            query = query.order_by(order_by)
        if limit:
            query = query.limit(limit)
        return query.all()
    
    def count(self, model: Type[T]) -> int:
        """统计实体数量"""
        return self.db.query(model).count()
