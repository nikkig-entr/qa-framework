"""Test data factories using Faker."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from faker import Faker

fake = Faker()


@dataclass
class UserFactory:
    """Factory for generating user test data."""

    username: str = field(default_factory=lambda: fake.user_name())
    email: str = field(default_factory=lambda: fake.email())
    password: str = field(default_factory=lambda: fake.password(length=12))
    first_name: str = field(default_factory=lambda: fake.first_name())
    last_name: str = field(default_factory=lambda: fake.last_name())
    phone: str = field(default_factory=lambda: fake.phone_number())
    address: dict[str, Any] = field(default_factory=lambda: {
        "street": fake.street_address(),
        "city": fake.city(),
        "zipcode": fake.zipcode(),
        "geo": {"lat": fake.latitude(), "lng": fake.longitude()},
    })
    company: dict[str, Any] = field(default_factory=lambda: {
        "name": fake.company(),
        "catch_phrase": fake.catch_phrase(),
        "bs": fake.bs(),
    })

    def to_dict(self) -> dict[str, Any]:
        return {
            "username": self.username,
            "email": self.email,
            "password": self.password,
            "firstName": self.first_name,
            "lastName": self.last_name,
            "phone": self.phone,
            "address": self.address,
            "company": self.company,
        }


@dataclass
class PostFactory:
    """Factory for generating post test data."""

    user_id: int = 1
    title: str = field(default_factory=lambda: fake.sentence(nb_words=6))
    body: str = field(default_factory=lambda: fake.paragraph(nb_sentences=3))

    def to_dict(self) -> dict[str, Any]:
        return {
            "userId": self.user_id,
            "title": self.title,
            "body": self.body,
        }


@dataclass
class CommentFactory:
    """Factory for generating comment test data."""

    post_id: int = 1
    name: str = field(default_factory=lambda: fake.name())
    email: str = field(default_factory=lambda: fake.email())
    body: str = field(default_factory=lambda: fake.paragraph(nb_sentences=2))

    def to_dict(self) -> dict[str, Any]:
        return {
            "postId": self.post_id,
            "name": self.name,
            "email": self.email,
            "body": self.body,
        }


def generate_users(count: int) -> list[dict[str, Any]]:
    """Generate multiple users."""
    return [UserFactory().to_dict() for _ in range(count)]


def generate_posts(count: int, user_id: int = 1) -> list[dict[str, Any]]:
    """Generate multiple posts."""
    return [PostFactory(user_id=user_id).to_dict() for _ in range(count)]


