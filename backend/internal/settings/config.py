"""Loading configs."""

import pathlib
from typing import Annotated, Literal

import yaml  # type: ignore[import-untyped]
from pydantic import BaseModel, Field, model_validator

from internal.settings.env import badges_settings


class BadgesConfig:
    """Badges config."""

    class BaseBadgeRule(BaseModel):
        """Base model for all badge rules."""

        level: int

    class QuantityGoal(BaseBadgeRule):
        """Badge rule for quantity."""

        type: Literal["quantity"]
        quantity: int

        category_id: int | None = None
        seller_id: int | None = None

    class CO2Goal(BaseBadgeRule):
        """Badge rule for carbon dioxide saving."""

        type: Literal["co2"]
        carbon_dioxide: float

    class DiversityGoal(BaseBadgeRule):
        """Badge rule for diverse reservations."""

        type: Literal["diversity"]
        dif_categories: int = 0
        dif_sellers: int = 0

        @model_validator(mode="after")
        def exclusive_validator(self) -> BadgesConfig.DiversityGoal:
            """Validates if no conflicting field are set.

            Returns:
                valid model

            Raises:
                ValueError: if model is not valid
            """
            if self.dif_categories < 1 and self.dif_sellers < 1:
                raise ValueError(
                    "Provide 'dif_categories' or 'dif_sellers' but not both"
                )
            if not self.dif_categories < 1 and not self.dif_sellers < 1:
                raise ValueError("Provide 'dif_categories' or 'dif_sellers'")
            if self.dif_categories < 0 or self.dif_sellers < 0:
                raise ValueError("Invalid negative value")
            return self

    class StreakGoal(BaseBadgeRule):
        """Badge rule for a steak of reservations."""

        type: Literal["streak"]
        streak_days: int = 0
        streak_quantity: int = 0

        category_id: int | None = None
        seller_id: int | None = None

        @model_validator(mode="after")
        def exclusive_validator(self) -> BadgesConfig.StreakGoal:
            """Validates if no conflicting field are set.

            Returns:
                valid model

            Raises:
                ValueError: if model is not valid
            """
            if self.streak_days < 1 and self.streak_quantity < 1:
                raise ValueError(
                    "Provide 'streak_days' or 'streak_quantity' but not both"
                )
            if not self.streak_days < 1 and not self.streak_quantity < 1:
                raise ValueError("Provide 'streak_days' or 'streak_quantity'")
            if self.streak_days < 0 or self.streak_quantity < 0:
                raise ValueError("Invalid negative value")
            return self

    BadgeGoal = Annotated[
        QuantityGoal | CO2Goal | DiversityGoal | StreakGoal, Field(discriminator="type")
    ]

    class BadgeRules(BaseModel):
        """Full badge rule set."""

        badge_id: int
        badge_name: str | None = None
        rules: list[BadgesConfig.BadgeGoal]

    class BadgesRules(BaseModel):
        """Rules for all badges."""

        badges_rules: list[BadgesConfig.BadgeRules]

    badges_rules: BadgesConfig.BadgesRules

    def initialise(self) -> None:
        """Load badges rules from file.

        Args:
          self: class instance
        """
        with pathlib.Path(badges_settings.rules_path).open(encoding="utf-8") as file:
            raw_data = yaml.safe_load(file)
            self.badges_rules = BadgesConfig.BadgesRules.model_validate(raw_data)


badges_config = BadgesConfig()
