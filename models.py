from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    role: Mapped[str] = mapped_column(String(20))

    # customer's tickets (as a user)
    tickets: Mapped[list["Ticket"]] = relationship(
        back_populates="user", foreign_keys="Ticket.user_id"
    )
    # tickets this user verified (as a clerk)
    verified_tickets: Mapped[list["Ticket"]] = relationship(
        back_populates="verifier", foreign_keys="Ticket.verified_by"
    )

    __table_args__ = (
        CheckConstraint("role IN ('customer', 'clerk')", name="ck_users_role"),
    )


class Service(db.Model):
    __tablename__ = "services"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80), unique=True)
    avg_minutes: Mapped[int]

    tickets: Mapped[list["Ticket"]] = relationship(back_populates="service")

    __table_args__ = (
        CheckConstraint("avg_minutes > 0", name="ck_services_avg_minutes"),
    )


class Ticket(db.Model):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"))
    service_id: Mapped[int] = mapped_column(ForeignKey("services.id", ondelete="RESTRICT"))
    status: Mapped[str] = mapped_column(String(20), default="waiting", server_default="waiting")
    priority_level: Mapped[str] = mapped_column(
        String(20), default="regular", server_default="regular"
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    called_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    verified_by: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"))
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # two foreign keys point at users, so each relationship names the one it uses
    user: Mapped["User"] = relationship(back_populates="tickets", foreign_keys=[user_id])
    verifier: Mapped["User | None"] = relationship(
        back_populates="verified_tickets", foreign_keys=[verified_by]
    )
    service: Mapped["Service"] = relationship(back_populates="tickets")

    __table_args__ = (
        CheckConstraint(
            "status IN ('waiting', 'called', 'served', 'completed', 'skipped', 'left')",
            name="ck_tickets_status",
        ),
        CheckConstraint(
            "priority_level IN ('regular', 'pwd')",
            name="ck_tickets_priority_level",
        ),
        CheckConstraint(
            "called_at IS NULL OR called_at >= created_at",
            name="ck_tickets_called_at",
        ),
    )