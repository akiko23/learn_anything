import uuid

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from learn_anything.adapters.persistence.tables.user import users_table, auth_links_table
from learn_anything.application.ports.data.auth_link_gateway import AuthLinkGateway
from learn_anything.application.ports.data.user_gateway import UserGateway
from learn_anything.entities.user.models import UserID, User, AuthLink


class UserMapper(UserGateway):
    def __init__(self, session: AsyncSession) -> None:
        self._session: AsyncSession = session

    async def save(self, user: User) -> None:
        stmt = (
            insert(users_table).
            values(
                id=user.id,
                role=user.role,
                username=user.username,
                fullname=user.fullname,
            )
        )

        if user.id:
            stmt = stmt.on_conflict_do_update(
                index_elements=['id'],
                set_=dict(
                    role=user.role
                ),
                where=(users_table.c.id == user.id)
            )

        await self._session.execute(stmt)

    async def with_id(self, user_id: UserID) -> User | None:
        stmt = select(User).where(users_table.c.id == user_id)
        result = await self._session.execute(stmt)

        return result.scalar_one_or_none()


class AuthLinkMapper(AuthLinkGateway):
    def __init__(self, session: AsyncSession) -> None:
        self._session: AsyncSession = session

    async def with_id(self, auth_link_id: uuid.UUID) -> AuthLink | None:
        stmt = select(AuthLink).where(auth_links_table.c.id == auth_link_id)
        result = await self._session.execute(stmt)

        return result.scalar_one_or_none()

    async def save(self, auth_link: AuthLink) -> uuid.UUID:
        upsert_stmt = (
            insert(auth_links_table).
            values(
                for_role=auth_link.for_role,
                usages=auth_link.usages,
                expires_at=auth_link.expires_at,
            ).on_conflict_do_update(
                constraint='auth_links_pkey',
                set_=dict(usages=auth_link.usages)
            ).returning(auth_links_table.c.id)
        )

        res = await self._session.execute(upsert_stmt)
        return res.scalar_one_or_none()

    async def delete(self, auth_link_id: uuid.UUID) -> None:
        stmt = select(AuthLink).where(auth_links_table.c.id == auth_link_id)
        await self._session.execute(stmt)
