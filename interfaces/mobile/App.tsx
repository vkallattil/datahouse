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
      <ScrollView style={styles.messagesContainer}>
        {chatMessages.map((message, index) => (
          <Text key={index}>{message.author}: {message.content}</Text>
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
    backgroundColor: '#fff',
    alignItems: 'center',
    paddingTop: 60,
    paddingBottom: 20,
  },
  messagesContainer: {
    flex: 1,
    width: '100%',
    paddingHorizontal: 10,
    marginBottom: 10,
  },
  inputContainer: {
    flexDirection: 'row',
    padding: 20,
    width: '100%',
    alignItems: 'center',
  },
  input: {
    flex: 1,
    borderWidth: 1,
    borderColor: '#ccc',
    borderRadius: 5,
    padding: 10,
    marginRight: 10,
  },
});
