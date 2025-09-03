import { StatusBar } from 'expo-status-bar';
import { StyleSheet, Text, View, TextInput, Button, ScrollView, KeyboardAvoidingView, Platform } from 'react-native';

import React, { useEffect, useRef, useState } from 'react';

import { Socket, io } from 'socket.io-client';

interface ChatMessage {
  author: string;
  content: string;
}

interface SocketMessage {
  type: "chat";
  message: ChatMessage;
  is_streaming: boolean;
}

export default function App() {
  const [status, setStatus] = useState('Disconnected');
  const [chatMessage, setChatMessage] = useState('');
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const socket = useRef<Socket | null>(null);
  // Track if we're currently streaming a message
  const isStreamingRef = useRef(false);

  useEffect(() => {
    socket.current = io('https://21adc1dd1a91.ngrok-free.app');

    socket.current.on('connect', () => {
      setStatus('Connected');
    });

    socket.current.on('disconnect', () => {
      setStatus('Disconnected');
    });

    socket.current.on("connect_error", (err) => {
      setStatus('Error');
    });

    socket.current.on('message', (data: SocketMessage) => {
      if (data.type === "chat") {
        if (data.is_streaming) {
          // If this is the first chunk of a new message, add a new message to the chat
          if (!isStreamingRef.current) {
            isStreamingRef.current = true;
            setChatMessages(prev => [...prev, {author: "assistant", content: data.message.content}]);
          } else {
            // Update the last message with the new content
            setChatMessages(prev => {
              const newMessages = [...prev];
              const lastIndex = newMessages.length - 1;
              newMessages[lastIndex] = {
                ...newMessages[lastIndex],
                content: newMessages[lastIndex].content + data.message.content
              };
              return newMessages;
            });
          }
        } else {
          // Final message, mark streaming as complete
          isStreamingRef.current = false;
        }
      }
    });

    return () => {
      socket.current?.disconnect();
    };
  }, []);

  return (
    <KeyboardAvoidingView 
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      style={styles.container}
    >
      <Text>Socket: {status}</Text>
      <ScrollView 
        style={styles.messagesContainer}
        contentContainerStyle={styles.messagesContent}
      >
        {chatMessages.map((message, index) => (
          <View 
            key={index} 
            style={[
              styles.messageBubble,
              message.author === 'client' ? styles.userBubble : styles.assistantBubble
            ]}
          >
            <Text style={[
              styles.messageText,
              message.author === 'client' && styles.userMessageText
            ]}>
              {message.content}
            </Text>
          </View>
        ))}
      </ScrollView>
      <View style={styles.inputContainer}>
        <TextInput 
          style={styles.input}
          placeholder="Enter message" 
          value={chatMessage} 
          onChangeText={setChatMessage} 
        />
        <Button 
          title="Send" 
          onPress={() => {
            if (chatMessage.trim()) {
              setChatMessages((prev) => [...prev, {author: "client", content: chatMessage}]);
              socket.current?.emit('message', {type: "chat", message: {author: "client", content: chatMessage}});
              setChatMessage('');
            }
          }} 
        />
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
    padding: 10,
    paddingTop: 60,
  },
  messagesContainer: {
    flex: 1,
    marginBottom: 10,
  },
  messagesContent: {
    padding: 10,
  },
  messageBubble: {
    maxWidth: '80%',
    padding: 12,
    borderRadius: 18,
    marginVertical: 4,
  },
  userBubble: {
    alignSelf: 'flex-end',
    backgroundColor: '#007AFF',
    borderTopRightRadius: 4,
  },
  assistantBubble: {
    alignSelf: 'flex-start',
    backgroundColor: '#e5e5ea',
    borderTopLeftRadius: 4,
  },
  messageText: {
    fontSize: 16,
  },
  userMessageText: {
    color: 'white',
  },
  inputContainer: {
    flexDirection: 'row',
    padding: 10,
    paddingBottom: 30
  },
  input: {
    flex: 1,
    borderWidth: 1,
    borderColor: '#ccc',
    borderRadius: 20,
    padding: 10,
    marginRight: 10,
    backgroundColor: '#fff',
  },
  button: {
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#007AFF',
    borderRadius: 20,
    paddingHorizontal: 20,
  },
  buttonText: {
    color: '#fff',
    fontWeight: 'bold',
  },
});
