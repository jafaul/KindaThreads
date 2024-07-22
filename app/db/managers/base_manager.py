from abc import ABC, abstractmethod
from datetime import datetime
from typing import TypeVar, Generic, Type, Optional

from pydantic import BaseModel
from sqlalchemy import select, and_, update, Select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas import user_schemas
from app.db.database import Base
from app.google_api_ai.controller import Controller

EntityType = TypeVar('EntityType', bound=BaseModel)
ModelType = TypeVar('ModelType', bound=Base)


class BaseManager(ABC, Generic[EntityType, ModelType]):
    def __init__(self, db: AsyncSession):
        self.db = db
        self._c = Controller()

    @property
    @abstractmethod
    def model_class(self) -> Type[ModelType]:
        pass

    async def create(self, entity_create: EntityType, owner_id: int, **kwargs) -> int:
        is_passed_validation = await self._c.check_for_inappropriate_content(entity_create.content)

        entity_instance = self.model_class(
            **entity_create.model_dump(),
            owner_id=owner_id,
            is_blocked=not is_passed_validation,
            **kwargs
        )

        try:
            async with self.db as async_session:
                self.db.add(entity_instance)
                await async_session.flush()
                await async_session.refresh(entity_instance)
                await async_session.commit()
        except Exception:
            await self.db.rollback()
            raise
        return entity_instance.id

    async def _get_many_by_query(
            self, query: Select
    ) -> list[ModelType] | None:
        async with self.db as async_session:
            result = await async_session.execute(query)
            entities = result.scalars().all()

        if not entities:
            return
        return list(entities)

    @abstractmethod
    async def get_many_by_entity_owner_id(
            self, entity_owner_id: int, from_: datetime, till_: datetime, visible_blocked: bool = False
    ) -> list[ModelType] | None:
        pass

    @abstractmethod
    async def get_many(self, date_from: datetime.date, date_to: datetime.date, user_id: int) -> list[ModelType]:
        pass

    async def get_one(self, id_: int, query: Optional[Select] = None) -> ModelType:
        if query is None:
            # set default
            query = select(self.model_class).where(
                        and_(
                            self.model_class.id == id_,
                        )
                    )

        async with self.db as async_session:
            result = await async_session.execute(
                query
            )
            entity_db = result.scalars().first()
        return entity_db

    async def update(self, id_: int, entity_create: EntityType) -> None:
        is_passed_validation = await self._c.check_for_inappropriate_content(entity_create.content)

        try:
            async with self.db as async_session:
                await async_session.execute(
                    update(self.model_class).where(
                        and_(
                            self.model_class.id == id_,
                        )
                    ).values(
                        **entity_create.model_dump(),
                        is_blocked=not is_passed_validation,
                        updated_at=datetime.utcnow()
                    )
                )
                await async_session.flush()
                await async_session.commit()
        except Exception:
            await async_session.rollback()
            raise

    async def delete(self, id_: int):
        try:
            async with self.db as async_session:
                entity = await self.get_one(id_)
                await async_session.delete(entity)
                await async_session.commit()
        except Exception:
            await async_session.rollback()
            raise

    @staticmethod
    def filter_by_blocked(entities: list[ModelType]) -> dict[str, list[ModelType]]:
        result = {
            "published": [],
            "blocked": []
        }
        for entity in entities:
            if entity.is_blocked:
                result["blocked"].append(entity)
            else:
                result["published"].append(entity)

        return result

    @abstractmethod
    def check_access_to_content(
        self,
        current_user: user_schemas.UserRead,
        post_owner_user_id: int,
        **kwargs
    ):
        pass
