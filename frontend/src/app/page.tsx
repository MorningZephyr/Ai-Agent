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
  is_owner: boolean;
  message: string;
}

interface ErrorInfo {
  status?: number;
  title?: string;
  message: string;
  detail?: any;
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  const [sessionInfo, setSessionInfo] = useState<SessionInfo | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [userId, setUserId] = useState('user_001');
  // owner concept removed
  const [error, setError] = useState<ErrorInfo | null>(null);
  const [debugOpen, setDebugOpen] = useState(false);
  const [health, setHealth] = useState<any | null>(null);
  const [sessionMeta, setSessionMeta] = useState<any | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  function parseAxiosError(err: any): ErrorInfo {
    if (axios.isAxiosError(err)) {
      const status = err.response?.status;
      const message = (err.response?.data?.detail) ?? err.message;
      const detail = err.response?.data ?? (typeof err.toJSON === 'function' ? err.toJSON() : String(err));
      return { status, title: 'Request failed', message: String(message), detail };
    }
    return { title: 'Error', message: err instanceof Error ? err.message : String(err) };
  }

  const refreshHealth = async () => {
    try {
      const res = await axios.get('http://localhost:8000/api/health');
      setHealth(res.data);
    } catch (e) {
      setError(parseAxiosError(e));
    }
  };

  const refreshSessionInfo = async () => {
    if (!sessionInfo) return;
    try {
      const res = await axios.get(`http://localhost:8000/api/session/${sessionInfo.session_id}/info`);
      setSessionMeta(res.data);
    } catch (e) {
      setError(parseAxiosError(e));
    }
  };

  const authenticateUser = async () => {
    try {
      setIsLoading(true);
      const response = await axios.post('http://localhost:8000/api/auth', {
        user_id: userId
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
  setError(parseAxiosError(error));
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
        message: inputText
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
  setError(parseAxiosError(error));
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
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const quickSend = async (text: string) => {
    setInputText(text);
    // slight delay to ensure state update then send
    setTimeout(sendMessage, 0);
  };

  const endSession = async () => {
    if (!sessionInfo) return;
    try {
      await axios.delete(`http://localhost:8000/api/session/${sessionInfo.session_id}`);
    } catch (err) {
      console.warn('Failed to end session on server, clearing client state.');
    }
    setSessionInfo(null);
    setMessages([]);
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
                <div className="mt-3 flex items-center gap-3 flex-wrap">
                  <span className="text-gray-100">Connected as</span>
                  <span className="px-2 py-1 rounded-md bg-cyan-600/30 border border-cyan-300/30 text-cyan-100">
                    {sessionInfo.user_id}
                  </span>
                  <span className={`px-2 py-1 rounded-md border bg-emerald-500/20 border-emerald-300/40 text-emerald-100`}>
                    Connected
                  </span>
                  <div className="ml-auto flex items-center gap-2">
                    <button onClick={() => setDebugOpen(v => !v)} className="bg-gray-900/30 hover:bg-gray-900/50 border border-gray-300/20 text-white text-sm px-3 py-1.5 rounded-md transition-colors">{debugOpen ? 'Hide' : 'Debug'}</button>
                    <button onClick={endSession} className="bg-red-500/80 hover:bg-red-500 text-white text-sm px-3 py-1.5 rounded-md transition-colors border border-red-300/40">End Session</button>
                  </div>
                </div>
            )}
          </div>
        </div>

          {/* Error Banner */}
          {error && (
            <div className="mx-6 mt-4 mb-2 rounded-lg border border-red-400/40 bg-red-900/30 text-red-100 p-4">
              <div className="flex items-start gap-3">
                <div className="font-semibold">{error.title || 'Error'}{typeof error.status === 'number' ? ` (${error.status})` : ''}</div>
                <div className="flex-1">{error.message}</div>
                <div className="flex items-center gap-2">
                  {error.detail && (
                    <button
                      onClick={async () => {
                        try {
                          await navigator.clipboard.writeText(JSON.stringify(error.detail, null, 2));
                        } catch {}
                      }}
                      className="text-xs px-2 py-1 rounded border border-red-300/40 hover:bg-red-900/40"
                    >Copy details</button>
                  )}
                  <button onClick={() => setError(null)} className="text-xs px-2 py-1 rounded border border-red-300/40 hover:bg-red-900/40">Dismiss</button>
                </div>
              </div>
              {error.detail && (
                <pre className="mt-2 max-h-48 overflow-auto text-xs whitespace-pre-wrap">{JSON.stringify(error.detail, null, 2)}</pre>
              )}
            </div>
          )}

          {/* Debug Panel */}
          {debugOpen && (
            <div className="mx-6 mb-4 rounded-lg border border-cyan-400/30 bg-cyan-900/10 text-cyan-100 p-4">
              <div className="flex items-center gap-2 mb-3">
                <button onClick={refreshHealth} className="text-xs px-2 py-1 rounded border border-cyan-300/40 hover:bg-cyan-900/20">Refresh Health</button>
                {sessionInfo && (
                  <button onClick={refreshSessionInfo} className="text-xs px-2 py-1 rounded border border-cyan-300/40 hover:bg-cyan-900/20">Refresh Session Info</button>
                )}
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <div>
                  <div className="text-sm font-semibold mb-1">Health</div>
                  <pre className="bg-black/30 rounded p-2 text-xs min-h-16">{health ? JSON.stringify(health, null, 2) : 'No data'}</pre>
                </div>
                <div>
                  <div className="text-sm font-semibold mb-1">Session Info</div>
                  <pre className="bg-black/30 rounded p-2 text-xs min-h-16">{sessionMeta ? JSON.stringify(sessionMeta, null, 2) : 'No data'}</pre>
                </div>
              </div>
            </div>
          )}

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
                {/* Owner field removed */}
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
            {/* Quick Actions */}
            <div className="px-6 pt-6 bg-gradient-to-b from-gray-800/30 to-gray-900/50 border-b border-gray-700/40">
              <div className="flex flex-wrap gap-2">
                <button onClick={() => quickSend('My favorite color is blue')} className="text-sm px-3 py-1.5 rounded-md border border-emerald-600/50 bg-emerald-700/30 hover:bg-emerald-700/50 text-emerald-100">Teach: favorite color = blue</button>
                <button onClick={() => quickSend('I work at Google')} className="text-sm px-3 py-1.5 rounded-md border border-emerald-600/50 bg-emerald-700/30 hover:bg-emerald-700/50 text-emerald-100">Teach: employer</button>
              </div>
            </div>
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
                  onKeyDown={handleKeyDown}
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
