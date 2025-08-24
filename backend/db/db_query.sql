-- Check sessions table for profile state
SELECT user_id, state FROM sessions WHERE user_id = 'Zhen';

-- Check user_states table for profile state  
SELECT user_id, state FROM user_states WHERE user_id = 'Zhen';
