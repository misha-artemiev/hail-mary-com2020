from fastapi import BackgroundTasks
from internal.queries.analytics import AsyncQuerier as AnalyticsQuerier
from internal.queries.analytics import GetGraphParams, CreateGraphParams
from internal.database.manager import database_manager

class AnalyticsProcesser:
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
        async for conn in database_manager.get_connection():
            analytics_querier = AnalyticsQuerier(conn)
            graph_types = analytics_querier.get_graphs_types()
            async for graph_type in graph_types:
                if (graph := await analytics_querier.get_graph(GetGraphParams(seller_id=seller_id, graph_type=graph_type.graph_type_id))) is not None:
                     analytics_querier.delete_graph_series(graph_id=graph.graph_id)
                if await analytics_querier.create_graph(CreateGraphParams(seller_id=seller_id, graph_type=graph_type.graph_type_id)) == None:
                    raise ValueError("Failed to create analytics graph")
