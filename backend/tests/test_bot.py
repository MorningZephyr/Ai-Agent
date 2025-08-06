"""
Tests for the UserAuthenticatedBot class.
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
    """Test cases for UserAuthenticatedBot."""
    
    def test_bot_initialization(self):
        """Test bot initialization with owner ID."""
        bot = UserAuthenticatedBot("test_user")
        assert bot.bot_owner_id == "test_user"
        assert bot.current_user_id is None
        assert bot.session_service is None
        assert bot.agent is None
        assert bot.runner is None
    
    def test_create_initial_state_owner(self):
        """Test initial state creation for bot owner."""
        bot = UserAuthenticatedBot("test_user")
        state = bot.create_initial_state("test_user")
        
        assert state["is_owner"] is True
        assert state["current_user"] == "test_user"
        assert state["bot_owner_id"] == "test_user"
        assert state["session_created"] is True
    
    def test_create_initial_state_visitor(self):
        """Test initial state creation for visitor."""
        bot = UserAuthenticatedBot("test_user")
        state = bot.create_initial_state("visitor")
        
        assert state["is_owner"] is False
        assert state["current_user"] == "visitor"
        assert state["bot_owner_id"] == "test_user"
        assert state["session_created"] is True
    
    @patch('src.core.bot.DatabaseSessionService')
    @patch('src.core.bot.Agent')
    @patch('src.core.bot.Runner')
    async def test_initialize_success(self, mock_runner, mock_agent, mock_db_service):
        """Test successful bot initialization."""
        # Setup mocks
        mock_db_service.return_value = Mock()
        mock_agent.return_value = Mock()
        mock_runner.return_value = Mock()
        
        bot = UserAuthenticatedBot("test_user")
        result = await bot.initialize()
        
        assert result is True
        assert bot.session_service is not None
        assert bot.agent is not None
        assert bot.runner is not None
    
    @patch('src.core.bot.DatabaseSessionService')
    async def test_initialize_failure(self, mock_db_service):
        """Test bot initialization failure."""
        # Make database service raise an exception
        mock_db_service.side_effect = Exception("Database connection failed")
        
        bot = UserAuthenticatedBot("test_user")
        result = await bot.initialize()
        
        assert result is False


if __name__ == "__main__":
    pytest.main([__file__])
