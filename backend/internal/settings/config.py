"""Loading configs."""

import pathlib

import yaml  # type: ignore[import-untyped]
from pydantic import BaseModel

from internal.settings.env import badges_settings


class BadgesConfig:
    """Badges config."""

    class StreakTime(BaseModel):
        """Streak time for badges."""

        days: int = 0
        weeks: int = 0
        month: int = 0
        years: int = 0

    class BadgeRule(BaseModel):
        """Rules for badges."""

        rule_name: str
        badge_id: int
        count: int
        category: int | None = None
        streak: BadgesConfig.StreakTime

    class BadgesRules(BaseModel):
        """List of all rules for all badges."""

        rules: list[BadgesConfig.BadgeRule]

    badges_rules: BadgesRules

    def initialise(self) -> None:
        """Load badges rules from file.

        Args:
          self: class instance
        """
        with pathlib.Path(badges_settings.rules_path).open(encoding="utf-8") as file:
            raw_data = yaml.safe_load(file)
            self.badges_rules = BadgesConfig.BadgesRules.model_validate(raw_data)


badges_config = BadgesConfig()
