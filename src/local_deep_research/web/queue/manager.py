"""Queue manager for handling research queue operations"""

from ...database.session_context import get_user_db_session
from ...database.models import QueuedResearch, ResearchHistory


class QueueManager:
    """Manages the research queue operations"""

    @staticmethod
    def get_queue_position(username, research_id):
        """
        Get the current queue position for a research

        Args:
            username: User who owns the research
            research_id: UUID of the research

        Returns:
            int: Current queue position or None if not in queue
        """
        with get_user_db_session(username) as session:
            queued = (
                session.query(QueuedResearch)
                .filter_by(username=username, research_id=research_id)
                .first()
            )

            if not queued:
                return None

            # Count how many are ahead in queue
            ahead_count = (
                session.query(QueuedResearch)
                .filter(
                    QueuedResearch.username == username,
                    QueuedResearch.position < queued.position,
                )
                .count()
            )

            return ahead_count + 1

    @staticmethod
    def get_user_queue(username):
        """
        Get all queued researches for a user

        Args:
            username: User to get queue for

        Returns:
            list: List of queued research info
        """
        with get_user_db_session(username) as session:
            queued_items = (
                session.query(QueuedResearch)
                .filter_by(username=username)
                .order_by(QueuedResearch.position)
                .all()
            )

            result = []
            for item in queued_items:
                # Get research info
                research = (
                    session.query(ResearchHistory)
                    .filter_by(id=item.research_id)
                    .first()
                )

                if research:
                    result.append(
                        {
                            "research_id": item.research_id,
                            "query": item.query,
                            "mode": item.mode,
                            "position": item.position,
                            "created_at": item.created_at.isoformat()
                            if item.created_at
                            else None,
                            "is_processing": item.is_processing,
                        }
                    )

            return result
