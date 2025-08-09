"""
Tests for the simplified UserAuthenticatedBot class.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core import UserAuthenticatedBot


class TestUserAuthenticatedBot:
    """Tests for minimal memory bot (no owner/guest logic)."""

    def test_bot_initialization(self):
        bot = UserAuthenticatedBot("any")
        assert bot.bot_owner_id == "any"
        assert bot.current_user_id is None
        assert bot.session_service is None
        assert bot.agent is None
        assert bot.runner is None

    def test_create_initial_state(self):
        bot = UserAuthenticatedBot("any")
        state = bot.create_initial_state("user_1")
        assert state["session_created"] is True
    
    @patch('src.core.bot.DatabaseSessionService')
    @patch('src.core.bot.Agent')
    @patch('src.core.bot.Runner')
    def test_initialize_success(self, mock_runner, mock_agent, mock_db_service):
        """Test successful bot initialization."""
        # Setup mocks
        mock_db_service.return_value = Mock()
        mock_agent.return_value = Mock()
        mock_runner.return_value = Mock()
    bot = UserAuthenticatedBot("any")
    result = asyncio.run(bot.initialize())
    assert result is True
    assert bot.session_service is not None
    assert bot.agent is not None
    assert bot.runner is not None
    
    @patch('src.core.bot.DatabaseSessionService')
    def test_initialize_failure(self, mock_db_service):
        """Test bot initialization failure."""
        # Make database service raise an exception
        mock_db_service.side_effect = Exception("Database connection failed")
    bot = UserAuthenticatedBot("any")
    result = asyncio.run(bot.initialize())
    assert result is False


if __name__ == "__main__":
    pytest.main([__file__])
