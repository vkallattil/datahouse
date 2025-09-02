import { StatusBar } from 'expo-status-bar';
import { StyleSheet, Text, View } from 'react-native';

import React, { useEffect, useState } from 'react';

export default function App() {
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [message, setMessage] = useState('Connecting to API...');

  useEffect(() => {
    // IMPORTANT: If running on a real device, replace 'localhost' with your computer's LAN IP
    const apiUrl = 'http://192.168.1.66:5000/datahouse';
    console.log('Attempting to connect to:', apiUrl);
    
    fetch(apiUrl)
      .then((res) => {
        console.log('Response status:', res.status);
        if (!res.ok) {
          return res.text().then(text => {
            console.error('API Error Response:', text);
            throw new Error(`API error: ${res.status} - ${text || 'No error details'}`);
          });
        }
        return res.text();
      })
      .then((text) => {
        console.log('API Response:', text);
        setStatus('success');
        setMessage(`API says: ${text}`);
      })
      .catch((err) => {
        console.error('Fetch Error:', err);
        setStatus('error');
        setMessage(`Failed to connect to API: ${err.message}`);
      });
  }, []);

  return (
    <View style={styles.container}>
      <Text>{message}</Text>
      <StatusBar style="auto" />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
    alignItems: 'center',
    justifyContent: 'center',
  },
});
