'use client'

import { useEffect, useRef, useState } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { useAppStore } from '@/lib/store'
import { sessions, documents, chat, SessionListItem } from '@/lib/api'
import { toast } from 'sonner'
import { 
  MessageCircle, Upload, Plus, Trash2, Send, Loader2, 
  FileText, Zap, Settings, LogOut, Menu, X
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Separator } from '@/components/ui/separator'
import { Skeleton } from '@/components/ui/skeleton'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog'

export default function Home() {
  const {
    sessionId,
    setSessionId,
    messages,
    addMessage,
    updateMessage,
    clearMessages,
    isLoading,
    setIsLoading,
  } = useAppStore()

  const [query, setQuery] = useState('')
  const [docInfo, setDocInfo] = useState<any>(null)
  const [sessionList, setSessionList] = useState<SessionListItem[]>([])
  const [sessionInfo, setSessionInfo] = useState<any>(null)
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [showNameDialog, setShowNameDialog] = useState(false)
  const [showClearAllDialog, setShowClearAllDialog] = useState(false)
  const [newSessionName, setNewSessionName] = useState('')
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    loadSessions()
  }, [])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  useEffect(() => {
    if (sessionId) {
      loadSessionData()
    }
  }, [sessionId])

  const loadSessions = async () => {
    try {
      const res = await sessions.list()
      console.log('Sessions loaded:', res.data)
      setSessionList(res.data || [])
    } catch (error: any) {
      console.error('Failed to load sessions:', error)
      toast.error('Failed to load sessions')
    }
  }

  const loadSessionData = async () => {
    if (!sessionId) return
    try {
      const [sessionRes, docsRes] = await Promise.all([
        sessions.get(sessionId),
        documents.get(sessionId),
      ])
      setSessionInfo(sessionRes.data)
      setDocInfo(docsRes.data)
    } catch (error: any) {
      toast.error('Failed to load session data')
    }
  }

  const promptForSessionName = () => {
    setNewSessionName('')
    setShowNameDialog(true)
  }

  const createSessionWithName = async () => {
    if (!newSessionName.trim()) {
      toast.error('Please enter a session name')
      return
    }

    try {
      const res = await sessions.create(newSessionName.trim())
      const newSessionId = res.data
      setSessionId(newSessionId)
      clearMessages()
      await loadSessions()
      setShowNameDialog(false)
      toast.success(`Session "${newSessionName}" created`)
    } catch (error: any) {
      toast.error('Failed to create session')
    }
  }

  const deleteSession = async () => {
    if (!sessionId) return
    try {
      await sessions.delete(sessionId)
      setSessionId(null)
      clearMessages()
      await loadSessions()
      toast.success('Session deleted')
    } catch (error: any) {
      toast.error('Failed to delete session')
    }
  }

  const clearAllSessions = async () => {
    try {
      const res = await sessions.deleteAll()
      setSessionId(null)
      clearMessages()
      await loadSessions()
      setShowClearAllDialog(false)
      toast.success(res.data?.message || 'All sessions cleared')
    } catch (error: any) {
      toast.error('Failed to clear sessions')
    }
  }

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!sessionId || !e.target.files) return

    const files = Array.from(e.target.files)
    setIsLoading(true)

    try {
      await documents.upload(sessionId, files)
      toast.success('Documents uploaded')
      await documents.index(sessionId)
      toast.success('Documents indexed')
      await loadSessionData()
      e.target.value = ''
    } catch (error: any) {
      toast.error('Failed to upload documents')
    } finally {
      setIsLoading(false)
    }
  }

  const handleSendQuery = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!sessionId || !query.trim() || isLoading) return

    const userQuery = query
    setQuery('')
    setIsLoading(true)

    try {
      addMessage({
        id: Date.now().toString(),
        role: 'user',
        content: userQuery,
        timestamp: new Date(),
      })

      // Add assistant message with empty content (will be filled with streamed tokens)
      const assistantMessageId = (Date.now() + 1).toString()
      addMessage({
        id: assistantMessageId,
        role: 'assistant',
        content: '',
        sources: [],
        timestamp: new Date(),
      })

      // Stop loading indicator now that streaming has started
      setIsLoading(false)

      let fullContent = ''
      let sources: string[] = []
      let tokenCount = 0

      // Stream tokens from the new endpoint
      for await (const message of chat.stream(sessionId, userQuery)) {
        if (message.type === 'token') {
          // Accumulate tokens
          fullContent += message.content
          tokenCount++
          
          console.log(`📨 Token ${tokenCount}: "${message.content}" (total: ${fullContent.length})`)
          
          // Update the message with new streamed content
          updateMessage(assistantMessageId, {
            content: fullContent,
          })
          
          // Add a tiny delay to allow React to render
          await new Promise(resolve => setTimeout(resolve, 0))
        } else if (message.type === 'metadata') {
          // Update sources
          console.log('📌 Metadata received:', message.sources)
          sources = message.sources || []
          updateMessage(assistantMessageId, {
            sources: sources,
          })
        } else if (message.type === 'error') {
          // Handle errors
          console.error('❌ Error received:', message.content)
          updateMessage(assistantMessageId, {
            content: `Error: ${message.content}`,
          })
          break
        }
      }
      
      console.log(`✅ Streaming complete. Total tokens: ${tokenCount}`)
    } catch (error: any) {
      toast.error('Failed to send query')
      setIsLoading(false)
    }
  }

  return (
    <div className="flex h-screen bg-background">
      {/* Sidebar */}
      <aside className={`${sidebarOpen ? 'w-64' : 'w-0'} border-r bg-slate-50 dark:bg-slate-900 transition-all duration-300 overflow-hidden flex flex-col`}>
        <div className="p-6 border-b">
          <div className="flex items-center gap-2 mb-4">
            <Zap className="w-6 h-6 text-blue-600" />
            <h1 className="text-xl font-bold">RAG Chat</h1>
          </div>
          <p className="text-sm text-muted-foreground">Powered by LM Studio</p>
        </div>

        <div className="flex-1 overflow-hidden flex flex-col p-4 space-y-4">
          <Button onClick={promptForSessionName} size="lg" className="w-full" disabled={isLoading}>
            <Plus className="w-4 h-4 mr-2" /> New Chat
          </Button>

          <div>
            <p className="text-sm font-semibold mb-3 text-muted-foreground">Recent Chats</p>
            <ScrollArea className="h-48">
              <div className="space-y-2 pr-4">
                {sessionList.filter(s => s && s.id).map((session) => {
                  const displayName = session.name || (session.id ? session.id.slice(0, 8) + '...' : 'Unnamed')
                  
                  return (
                    <Button
                      key={session.id}
                      variant={sessionId === session.id ? 'default' : 'ghost'}
                      size="sm"
                      onClick={() => setSessionId(session.id!)}
                      className="w-full justify-start text-xs truncate"
                      title={session.name || session.id || 'Unnamed session'}
                    >
                      <MessageCircle className="w-3 h-3 mr-2 flex-shrink-0" />
                      <span className="truncate">
                        {displayName}
                      </span>
                    </Button>
                  )
                })}
              </div>
            </ScrollArea>
            
            {sessionList.length > 0 && (
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowClearAllDialog(true)}
                className="w-full mt-2 text-destructive hover:text-destructive"
              >
                <Trash2 className="w-3 h-3 mr-2" />
                Clear All Sessions
              </Button>
            )}
          </div>
        </div>

        {sessionId && (
          <div className="p-4 border-t space-y-3">
            <Card className="p-3">
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Docs:</span>
                  <Badge variant="secondary">{sessionInfo?.documents?.length || 0}</Badge>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Chunks:</span>
                  <Badge variant="secondary">{sessionInfo?.indexed_chunks || 0}</Badge>
                </div>
              </div>
            </Card>
            <Button 
              onClick={deleteSession} 
              variant="destructive" 
              size="sm" 
              className="w-full"
            >
              <Trash2 className="w-4 h-4 mr-2" /> Delete Chat
            </Button>
          </div>
        )}
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col">
        {/* Header */}
        <header className="border-b bg-background sticky top-0 z-10">
          <div className="flex items-center justify-between p-4">
            <Button 
              variant="ghost" 
              size="icon" 
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="lg:hidden"
            >
              {sidebarOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </Button>
            <div className="flex-1 text-center">
              {sessionId && (
                <p className="text-sm text-muted-foreground">
                  Session: <span className="font-mono text-xs">{sessionId.slice(0, 12)}...</span>
                </p>
              )}
            </div>
            <div className="w-8" />
          </div>
        </header>

        {!sessionId ? (
          <div className="flex-1 flex items-center justify-center p-8">
            <div className="text-center max-w-md">
              <div className="mb-6 flex justify-center">
                <div className="p-4 rounded-full bg-blue-100 dark:bg-blue-900">
                  <MessageCircle className="w-8 h-8 text-blue-600" />
                </div>
              </div>
              <h2 className="text-3xl font-bold mb-2">Welcome to RAG Chat</h2>
              <p className="text-muted-foreground mb-8">
                Start a new conversation to upload documents and explore them with AI.
              </p>
              <Button size="lg" onClick={promptForSessionName}>
                <Plus className="w-4 h-4 mr-2" /> Create New Chat
              </Button>
            </div>
          </div>
        ) : (
          <>
            {/* Documents Section */}
            <div className="border-b bg-background p-4">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-semibold flex items-center gap-2">
                  <FileText className="w-4 h-4" /> Documents
                </h3>
                <label className="cursor-pointer">
                  <Button size="sm" asChild>
                    <span>
                      <Upload className="w-4 h-4 mr-2" /> Upload
                    </span>
                  </Button>
                  <input
                    type="file"
                    multiple
                    accept=".pdf,.txt,.md,.html"
                    onChange={handleUpload}
                    disabled={isLoading}
                    className="hidden"
                  />
                </label>
              </div>
              
              {docInfo?.documents && docInfo.documents.length > 0 ? (
                <div className="flex flex-wrap gap-2">
                  {docInfo.documents.map((doc: any) => (
                    <Badge key={doc.filename} variant="outline" className="text-xs">
                      <FileText className="w-3 h-3 mr-1" />
                      {doc.filename.slice(0, 20)}...
                    </Badge>
                  ))}
                </div>
              ) : (
                <Alert>
                  <AlertDescription className="text-sm">
                    No documents uploaded yet. Upload documents to get started.
                  </AlertDescription>
                </Alert>
              )}
            </div>

            {/* Chat Area */}
            <div className="flex-1 flex flex-col min-h-0">
              <ScrollArea className="flex-1 p-4">
                <div className="space-y-4 max-w-4xl mx-auto">
                  {messages.length === 0 ? (
                    <div className="text-center text-muted-foreground py-12">
                      <MessageCircle className="w-12 h-12 mx-auto mb-4 opacity-20" />
                      <p>No messages yet. Start a conversation!</p>
                    </div>
                  ) : (
                    messages.map((msg) => (
                      <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                        <div className={`flex gap-3 max-w-md ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
                          {msg.role === 'assistant' && (
                            <Avatar className="w-8 h-8 flex-shrink-0">
                              <AvatarFallback className="bg-blue-600 text-white text-xs">AI</AvatarFallback>
                            </Avatar>
                          )}
                          <Card className={msg.role === 'user' ? 'bg-blue-500 text-white border-blue-500 shadow-md' : 'bg-slate-800 text-white'}>
                            <CardContent className="p-3">
                              <div className={`prose ${msg.role === 'assistant' ? 'prose-invert' : ''} max-w-none prose-sm`}>
                                {!msg.content && msg.role === 'assistant' && (
                                  <span className="inline-block w-2 h-4 bg-blue-400 animate-pulse rounded-sm"></span>
                                )}
                                <ReactMarkdown 
                                  remarkPlugins={[remarkGfm]}
                                  components={{
                                    h1: ({node, ...props}) => <h1 className="text-lg font-bold my-2 text-white" {...props} />,
                                    h2: ({node, ...props}) => <h2 className="text-base font-bold my-2 text-white" {...props} />,
                                    h3: ({node, ...props}) => <h3 className="text-sm font-bold my-1 text-white" {...props} />,
                                    p: ({node, ...props}) => <p className="my-1 text-white" {...props} />,
                                    ul: ({node, ...props}) => <ul className="list-disc list-inside my-1 text-white" {...props} />,
                                    ol: ({node, ...props}) => <ol className="list-decimal list-inside my-1 text-white" {...props} />,
                                    li: ({node, ...props}) => <li className="my-0.5 ml-2 text-white" {...props} />,
                                    code: ({node, inline, ...props}) => 
                                      inline ? 
                                        <code className={`${msg.role === 'user' ? 'bg-blue-600' : 'bg-gray-700'} px-1 rounded text-xs text-white`} {...props} /> :
                                        <code className={`block ${msg.role === 'user' ? 'bg-blue-600' : 'bg-gray-700'} p-2 rounded text-xs overflow-x-auto text-white my-1`} {...props} />,
                                    blockquote: ({node, ...props}) => <blockquote className="border-l-4 border-gray-400 pl-3 italic my-1 text-white" {...props} />,
                                    a: ({node, ...props}) => <a className="text-cyan-300 underline hover:text-cyan-200" {...props} />,
                                  }}
                                >
                                  {msg.content}
                                </ReactMarkdown>
                              </div>
                              {msg.sources && msg.sources.length > 0 && (
                                <div className="mt-3 pt-3 border-t border-opacity-20">
                                  <p className="text-xs font-semibold mb-1 opacity-75">Sources:</p>
                                  <div className="space-y-1">
                                    {msg.sources.map((src) => (
                                      <Badge key={src} variant="secondary" className="text-xs">
                                        {src.split('/').pop()?.slice(0, 30)}...
                                      </Badge>
                                    ))}
                                  </div>
                                </div>
                              )}
                            </CardContent>
                          </Card>
                        </div>
                      </div>
                    ))
                  )}
                  {isLoading && (
                    <div className="flex justify-start">
                      <div className="flex gap-3">
                        <Avatar className="w-8 h-8 flex-shrink-0">
                          <AvatarFallback className="bg-blue-600 text-white text-xs">AI</AvatarFallback>
                        </Avatar>
                        <Card>
                          <CardContent className="p-3">
                            <div className="flex gap-2">
                              <Skeleton className="h-4 w-12" />
                              <Skeleton className="h-4 w-12" />
                              <Skeleton className="h-4 w-12" />
                            </div>
                          </CardContent>
                        </Card>
                      </div>
                    </div>
                  )}
                  <div ref={messagesEndRef} />
                </div>
              </ScrollArea>

              {/* Input Area */}
              <div className="border-t bg-background p-4">
                <form onSubmit={handleSendQuery} className="max-w-4xl mx-auto flex gap-2">
                  <Input
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="Ask a question about your documents..."
                    disabled={isLoading}
                    className="flex-1"
                  />
                  <Button 
                    type="submit" 
                    disabled={isLoading || !query.trim()}
                    size="icon"
                  >
                    {isLoading ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                      <Send className="w-4 h-4" />
                    )}
                  </Button>
                </form>
              </div>
            </div>
          </>
        )}
      </main>

      {/* Session Name Dialog */}
      <Dialog open={showNameDialog} onOpenChange={setShowNameDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Name Your Chat Session</DialogTitle>
            <DialogDescription>
              Give this chat session a memorable name to help you find it later.
            </DialogDescription>
          </DialogHeader>
          <div className="py-4">
            <Input
              placeholder="e.g., Research Notes, Client Project, Personal..."
              value={newSessionName}
              onChange={(e) => setNewSessionName(e.target.value)}
              onKeyPress={(e) => {
                if (e.key === 'Enter') {
                  createSessionWithName()
                }
              }}
              autoFocus
            />
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowNameDialog(false)}>
              Cancel
            </Button>
            <Button onClick={createSessionWithName} disabled={!newSessionName.trim()}>
              Create Session
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Clear All Sessions Confirmation Dialog */}
      <Dialog open={showClearAllDialog} onOpenChange={setShowClearAllDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Clear All Sessions?</DialogTitle>
            <DialogDescription>
              This will permanently delete all {sessionList.length} session{sessionList.length !== 1 ? 's' : ''} and their data including:
              <ul className="list-disc list-inside mt-2 space-y-1">
                <li>All uploaded documents</li>
                <li>Chat history</li>
                <li>Vector embeddings</li>
              </ul>
              <p className="mt-2 font-semibold text-destructive">This action cannot be undone!</p>
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowClearAllDialog(false)}>
              Cancel
            </Button>
            <Button variant="destructive" onClick={clearAllSessions}>
              <Trash2 className="w-4 h-4 mr-2" />
              Clear All Sessions
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
