from sqlalchemy import (
    Column,
    Integer,
    BigInteger,
    String,
    Text,
    Boolean,
    ForeignKey,
    DateTime,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from bot.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    language_code = Column(String(5), default="uz")  # 'uz', 'ru', 'en'
    full_name = Column(String(255), nullable=True)
    username = Column(String(255), nullable=True)
    is_staff = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    username = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    messages = relationship("Message", back_populates="group")


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    telegram_message_id = Column(Integer, nullable=False, index=True)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False)
    user_id = Column(BigInteger, nullable=True, index=True)
    full_name = Column(String(255), nullable=True)
    username = Column(String(255), nullable=True)
    text = Column(Text, nullable=True)

    is_question = Column(Boolean, default=False)
    is_answered = Column(Boolean, default=False)
    answered_by_bot = Column(Boolean, default=False)
    is_staff = Column(Boolean, default=False)

    # [NEW] AI Usage Tracking
    ai_provider = Column(String(50), nullable=True) # openai, groq, gemini
    ai_model = Column(String(100), nullable=True)
    prompt_tokens = Column(Integer, default=0)
    completion_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)

    reply_to_message_id = Column(Integer, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    group = relationship("Group", back_populates="messages")

    @property
    def telegram_link(self):
        if not self.group:
            return None
        if self.group.username:
            username = self.group.username.lstrip('@')
            return f"https://t.me/{username}/{self.telegram_message_id}"
        elif self.group.telegram_id:
            chat_id_str = str(self.group.telegram_id)
            if chat_id_str.startswith("-100"):
                chat_id_str = chat_id_str[4:]
        return f"https://t.me/c/{chat_id_str}/{self.telegram_message_id}"
        return None

    @property
    def telegram_app_link(self):
        if not self.group:
            return None
        if self.group.username:
            username = self.group.username.lstrip('@')
            return f"tg://resolve?domain={username}&post={self.telegram_message_id}"
        elif self.group.telegram_id:
            chat_id_str = str(self.group.telegram_id)
            if chat_id_str.startswith("-100"):
                chat_id_str = chat_id_str[4:]
            return f"tg://privatepost?channel={chat_id_str}&post={self.telegram_message_id}"
        return None


class KnowledgeBase(Base):
    __tablename__ = "knowledge_base"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())



class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)


class Setting(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(255), unique=True, nullable=False, index=True)
    value = Column(Text, nullable=True)

class ScheduledBroadcast(Base):
    __tablename__ = "scheduled_broadcasts"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    target_group_id = Column(Integer, ForeignKey("groups.id"), nullable=True)
    scheduled_at = Column(DateTime(timezone=True), nullable=False)
    status = Column(String(50), default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)                      # Kompaniya nomi
    logo_url = Column(String(500), nullable=True)                   # Logo (URL yoki fayl nomi)
    brand_name = Column(String(255), nullable=True)                 # Brand nomi
    main_currency = Column(String(10), default="UZS")              # Asosiy valyuta
    extra_currency = Column(String(10), nullable=True)              # Qo'shimcha valyuta
    phone = Column(String(30), nullable=True)                       # Telefon (+998...)
    director = Column(String(255), nullable=True)                   # Direktor
    responsible_name = Column(String(255), nullable=True)           # Mas'ul xodim
    responsible_phone = Column(String(30), nullable=True)           # Mas'ul xodim telefon
    status = Column(String(50), default="Yangi")                   # Yangi / Faol / To'xtatilgan / Bekor qilingan
    subscription_start = Column(DateTime(timezone=True), nullable=True)  # Obuna boshlanishi
    subscription_end = Column(DateTime(timezone=True), nullable=True)    # Obuna tugashi
    is_active = Column(Boolean, default=True)                       # Yoqilgan / O'chirilgan
    created_at = Column(DateTime(timezone=True), server_default=func.now())