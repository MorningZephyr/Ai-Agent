'use client';

import { useState, useEffect, useRef } from 'react';
import axios from 'axios';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'bot';
  timestamp: Date;
}

interface SessionInfo {
  session_id: string;
  user_id: string;
  bot_owner_id: string;
  is_owner: boolean;
  message: string;
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  const [sessionInfo, setSessionInfo] = useState<SessionInfo | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [userId, setUserId] = useState('user_001');
  const [botOwner, setBotOwner] = useState('zhen');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const authenticateUser = async () => {
    try {
      setIsLoading(true);
      const response = await axios.post('http://localhost:8000/api/auth', {
        user_id: userId,
        bot_owner_id: botOwner
      });
      
      setSessionInfo(response.data);
      setMessages([{
        id: '1',
        text: `${response.data.message}. You can now start chatting!`,
        sender: 'bot',
        timestamp: new Date()
      }]);
    } catch (error) {
      console.error('Authentication failed:', error);
      alert('Failed to connect to bot. Make sure the backend is running.');
    } finally {
      setIsLoading(false);
    }
  };

  const sendMessage = async () => {
    if (!inputText.trim() || !sessionInfo || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text: inputText,
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setIsLoading(true);

    try {
      const response = await axios.post(`http://localhost:8000/api/chat/${sessionInfo.session_id}`, {
        message: inputText,
        user_id: userId
      });

      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: response.data.response,
        sender: 'bot',
        timestamp: new Date()
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: 'Sorry, there was an error processing your message.',
        sender: 'bot',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-blue-900 p-4">
      <div className="max-w-4xl mx-auto bg-gray-800/90 backdrop-blur-sm rounded-xl shadow-2xl border border-gray-700/50">
        {/* Header */}
        <div className="bg-gradient-to-r from-purple-600 via-blue-600 to-cyan-500 text-white p-6 rounded-t-xl relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-r from-purple-600/20 via-blue-600/20 to-cyan-500/20 backdrop-blur-sm"></div>
          <div className="relative z-10">
            <h1 className="text-3xl font-bold bg-gradient-to-r from-white to-cyan-100 bg-clip-text text-transparent">
              🤖 Zhen Bot - ADK Test Interface
            </h1>
            {sessionInfo && (
              <p className="text-gray-100 mt-2">
                Connected as: <span className="font-semibold text-cyan-200">{sessionInfo.user_id}</span>
                <span className="mx-2">{sessionInfo.is_owner ? '👑 Owner' : '👤 Visitor'}</span> | 
                Bot Owner: <span className="font-semibold text-purple-200">{sessionInfo.bot_owner_id}</span>
              </p>
            )}
          </div>
        </div>

        {/* Authentication Section */}
        {!sessionInfo && (
          <div className="p-8 border-b border-gray-700/50 bg-gradient-to-br from-gray-800/50 to-gray-900/30">
            <div className="text-center mb-8">
              <h2 className="text-2xl font-bold text-gray-100 mb-2">🚀 Connect to Your AI Assistant</h2>
              <p className="text-gray-400">Enter your credentials to start an intelligent conversation</p>
            </div>
            
            <div className="max-w-md mx-auto space-y-6">
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Your User ID:</label>
                  <input
                    type="text"
                    value={userId}
                    onChange={(e) => setUserId(e.target.value)}
                    className="w-full bg-gray-700/50 border border-gray-600/50 text-gray-100 rounded-lg px-4 py-3 focus:border-cyan-400 focus:ring-2 focus:ring-cyan-400/20 focus:outline-none transition-all duration-200 placeholder-gray-400"
                    placeholder="user_001"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Bot Owner:</label>
                  <input
                    type="text"
                    value={botOwner}
                    onChange={(e) => setBotOwner(e.target.value)}
                    className="w-full bg-gray-700/50 border border-gray-600/50 text-gray-100 rounded-lg px-4 py-3 focus:border-purple-400 focus:ring-2 focus:ring-purple-400/20 focus:outline-none transition-all duration-200 placeholder-gray-400"
                    placeholder="zhen"
                  />
                </div>
              </div>
              
              <button
                onClick={authenticateUser}
                disabled={isLoading}
                className="w-full bg-gradient-to-r from-purple-600 via-blue-600 to-cyan-500 text-white px-6 py-4 rounded-lg hover:from-purple-700 hover:via-blue-700 hover:to-cyan-600 disabled:opacity-50 transition-all duration-300 font-semibold text-lg shadow-lg hover:shadow-xl hover:scale-[1.02] disabled:hover:scale-100"
              >
                {isLoading ? (
                  <span className="flex items-center justify-center">
                    <span className="animate-spin mr-2">⚡</span>
                    Connecting...
                  </span>
                ) : (
                  <span className="flex items-center justify-center">
                    <span className="mr-2">🔗</span>
                    Connect to Bot
                  </span>
                )}
              </button>
            </div>
          </div>
        )}

        {/* Chat Messages */}
        {sessionInfo && (
          <>
            <div className="h-96 overflow-y-auto p-6 space-y-4 bg-gradient-to-b from-gray-800/30 to-gray-900/50 backdrop-blur-sm">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-xs lg:max-w-md px-4 py-3 rounded-xl shadow-lg backdrop-blur-sm ${
                      message.sender === 'user'
                        ? 'bg-gradient-to-r from-purple-600/90 to-blue-600/90 text-white ml-4 border border-purple-400/30'
                        : 'bg-gradient-to-r from-cyan-500/20 to-emerald-500/20 border border-cyan-400/30 text-gray-100 mr-4'
                    }`}
                  >
                    <p className="whitespace-pre-wrap leading-relaxed">{message.text}</p>
                    <p className={`text-xs mt-2 ${
                      message.sender === 'user' 
                        ? 'text-purple-200' 
                        : 'text-cyan-300'
                    }`}>
                      {message.timestamp.toLocaleTimeString()}
                    </p>
                  </div>
                </div>
              ))}
              {isLoading && (
                <div className="flex justify-start">
                  <div className="bg-gradient-to-r from-amber-500/20 to-orange-500/20 border border-amber-400/30 text-amber-200 px-4 py-3 rounded-xl mr-4 shadow-lg backdrop-blur-sm">
                    <p className="flex items-center">
                      <span className="animate-pulse text-amber-400">✨</span>
                      <span className="ml-2 font-medium">Zhen Bot is thinking...</span>
                    </p>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Input Section */}
            <div className="p-4 border-t border-gray-700/50 bg-gradient-to-r from-gray-800/50 to-gray-900/30 backdrop-blur-sm">
              <div className="flex gap-3">
                <textarea
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Type your message... (Press Enter to send)"
                  className="flex-1 bg-gray-700/50 text-gray-100 border-2 border-gray-600/50 rounded-lg px-4 py-3 resize-none focus:border-cyan-400 focus:ring-2 focus:ring-cyan-400/20 focus:outline-none shadow-sm placeholder-gray-400 backdrop-blur-sm transition-all duration-200"
                  rows={2}
                />
                <button
                  onClick={sendMessage}
                  disabled={!inputText.trim() || isLoading}
                  className="bg-gradient-to-r from-purple-600 to-cyan-500 text-white px-6 py-3 rounded-lg hover:from-purple-700 hover:to-cyan-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 font-medium min-w-[80px] shadow-lg hover:shadow-xl hover:scale-105 disabled:hover:scale-100"
                >
                  {isLoading ? '⚡' : '🚀'}
                </button>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
