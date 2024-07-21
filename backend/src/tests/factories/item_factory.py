import factory
from sqlmodel import SQLModel

from src.models import Item
from src.tests.factories.base_factory import BaseFactory


class ItemFactory(BaseFactory):
    class Meta:
        model = Item

    title: str = factory.Faker("word")
    description: str = factory.Faker("sentence", nb_words=4)
