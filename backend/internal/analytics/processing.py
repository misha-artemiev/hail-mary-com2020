from fastapi import BackgroundTasks

class BadgeEngine:
    """Analytics processing."""

    background_tasks: BackgroundTasks

    def __init__(self, background_tasks: BackgroundTasks) -> None:
        """Init processing for seller"""
        self.background_tasks = background_tasks

    def run(self, seller_id: int) -> None:
        """Starts background analytics task.

        Args:
            seller_id: seller id
        """
        self.background_tasks.add_task(self.process_analytics, seller_id)

    @staticmethod
    async def process_analytics(seller_id: int):
        pass
