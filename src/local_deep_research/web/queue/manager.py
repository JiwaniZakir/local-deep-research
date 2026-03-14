"""Queue manager for handling research queue operations"""

from loguru import logger
from sqlalchemy import func

from ...database.session_context import get_user_db_session
from ...database.models import QueuedResearch, ResearchHistory


class QueueManager:
    """Manages the research queue operations"""

    @staticmethod
    def add_to_queue(
        username, research_id, query, mode, settings, db_session=None
    ):
        """
        Add a research to the queue

        Args:
            username: User who owns the research
            research_id: UUID of the research
            query: Research query
            mode: Research mode
            settings: Research settings dictionary
            db_session: Optional database session. When provided, the caller
                controls the transaction (no commit). When None, opens its own
                session and commits internally.

        Returns:
            int: Queue position
        """
        if db_session is not None:
            return QueueManager._add_to_queue_with_session(
                db_session, username, research_id, query, mode, settings
            )

        with get_user_db_session(username) as session:
            position = QueueManager._add_to_queue_with_session(
                session, username, research_id, query, mode, settings
            )
            session.commit()
            return position

    @staticmethod
    def _add_to_queue_with_session(
        session, username, research_id, query, mode, settings
    ):
        """Internal helper that performs queue add on a given session without committing."""
        # Get the next position in queue for this user
        max_position = (
            session.query(func.max(QueuedResearch.position))
            .filter_by(username=username)
            .scalar()
            or 0
        )

        queued_record = QueuedResearch(
            username=username,
            research_id=research_id,
            query=query,
            mode=mode,
            settings_snapshot=settings,
            position=max_position + 1,
        )
        session.add(queued_record)

        logger.info(
            f"Added research {research_id} to queue at position {max_position + 1}"
        )

        # Send RESEARCH_QUEUED notification if enabled
        try:
            from ...settings import SettingsManager
            from ...notifications import send_queue_notification

            settings_manager = SettingsManager(session)
            settings_snapshot = settings_manager.get_settings_snapshot()

            send_queue_notification(
                username=username,
                research_id=research_id,
                query=query,
                settings_snapshot=settings_snapshot,
                position=max_position + 1,
            )
        except Exception as e:
            logger.debug(f"Failed to send queued notification: {e}")

        return max_position + 1

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
    def remove_from_queue(username, research_id, db_session=None):
        """
        Remove a research from the queue

        Args:
            username: User who owns the research
            research_id: UUID of the research
            db_session: Optional database session. When provided, the caller
                controls the transaction (no commit). When None, opens its own
                session and commits internally.

        Returns:
            bool: True if removed, False if not found
        """
        if db_session is not None:
            return QueueManager._remove_from_queue_with_session(
                db_session, username, research_id
            )

        with get_user_db_session(username) as session:
            result = QueueManager._remove_from_queue_with_session(
                session, username, research_id
            )
            if result:
                session.commit()
            return result

    @staticmethod
    def _remove_from_queue_with_session(session, username, research_id):
        """Internal helper that performs queue removal on a given session without committing."""
        queued = (
            session.query(QueuedResearch)
            .filter_by(username=username, research_id=research_id)
            .first()
        )

        if not queued:
            return False

        position = queued.position
        session.delete(queued)

        # Update positions of items behind in queue
        session.query(QueuedResearch).filter(
            QueuedResearch.username == username,
            QueuedResearch.position > position,
        ).update({QueuedResearch.position: QueuedResearch.position - 1})

        logger.info(f"Removed research {research_id} from queue")
        return True

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
