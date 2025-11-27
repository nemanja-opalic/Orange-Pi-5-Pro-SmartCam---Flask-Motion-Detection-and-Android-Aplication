import React, { useEffect, useRef } from "react";
import { StyleSheet, Platform, Alert, ToastAndroid, Text, View } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { WebView } from "react-native-webview";

const FLASK_HOST = "192.168.1.130";
const VIDEO_URL = `http://${FLASK_HOST}:8000/video_feed`;
const EVENTS_URL = `http://${FLASK_HOST}:8000/evidencija.json`; // fajl na serveru

export default function App() {
  const lastNotificationTime = useRef(0);

  useEffect(() => {
  const interval = setInterval(async () => {
    try {
      const res = await fetch(EVENTS_URL);
      if (!res.ok) return;
      const events = await res.json();
      if (!Array.isArray(events) || events.length === 0) return;

      const lastEvent = events[events.length - 1];
      if (lastEvent.type === "motion") {
        const eventTime = new Date(lastEvent.timestamp).getTime();
        if (eventTime > lastNotificationTime.current) {
          // prikaži notifikaciju
          if (Platform.OS === "android") {
            ToastAndroid.show("Detektovan pokret!", ToastAndroid.SHORT);
          } else {
            Alert.alert("SmartCamAPP", "Detektovan pokret!");
          }
          lastNotificationTime.current = eventTime; // update na timestamp event-a
        }
      }
    } catch (err) {
      console.log("Error fetching events:", err);
    }
  }, 1500);

  return () => clearInterval(interval);
}, []);

  return (
    <SafeAreaView style={styles.container}>
      <Text style={styles.title}>SmartCamAPP</Text>
      <View style={styles.videoWrap}>
        <WebView
          source={{ uri: VIDEO_URL }}
          style={styles.video}
          allowsInlineMediaPlayback
          mediaPlaybackRequiresUserAction={false}
        />
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#d4e7ff", // nova pozadina
    alignItems: "center",
    paddingTop: 12,
  },
  title: {
    fontSize: 24,
    fontWeight: "700",
    marginBottom: 12,
    color: "#1a1a1a",
  },
  videoWrap: {
    width: "95%",
    height: 320,
    borderRadius: 12,
    overflow: "hidden",
    borderWidth: 2,
    borderColor: "#122",
  },
  video: {
    flex: 1,
  },
});
