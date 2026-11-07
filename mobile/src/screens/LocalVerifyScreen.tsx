import React from "react";
import { View, Text, StyleSheet, TouchableOpacity, ActivityIndicator } from "react-native";
import * as ImagePicker from "expo-image-picker";
import { Camera, CameraView } from "expo-camera";
import { api } from "../api/client";
import { ENDPOINTS } from "../api/endpoints";

export default function LocalVerifyScreen() {
  const [camera, setCamera] = React.useRef<CameraView>(null);
  const [hasPermission, setHasPermission] = React.useState<boolean | null>(null);
  const [uri, setUri] = React.useState<string | null>(null);
  const [submitting, setSubmitting] = React.useState(false);

  React.useEffect(() => {
    (async () => {
      const { status } = await Camera.requestCameraPermissionAsync();
      setHasPermission(status === "granted");
    })();
  }, []);

  const handlePickImage = async () => {
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      aspect: [4, 3],
    });
    if (!result.canceled && result.assets[0]) {
      setUri(result.assets[0].uri);
    }
  };

  const handleSubmit = async () => {
    if (!uri) return;
    setSubmitting(true);
    const form = new FormData();
    form.append("file", {
      uri,
      type: "image/jpeg",
      name: "probe.jpg",
    } as any);
    try {
      await api.postForm(ENDPOINTS.verify.local, form);
    } finally {
      setSubmitting(false);
    }
  };

  if (hasPermission === null) {
    return <ActivityIndicator size="small" />;
  }
  if (hasPermission === false) {
    return <Text>No camera permission</Text>;
  }

  return (
    <View style={styles.container}>
      <Camera style={styles.preview} ref={camera} />
      {uri && <Image source={{ uri }} style={styles.selected} />}
      <TouchableOpacity style={styles.button} onPress={handlePickImage}>
        <Text>Select from Gallery</Text>
      </TouchableOpacity>
      <TouchableOpacity style={styles.button} onPress={handleSubmit} disabled={submitting}>
        <Text>{submitting ? "Searching..." : "Run Local Verify"}</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#000" },
  preview: { flex: 1 },
  selected: { position: "absolute", top: 0, left: 0, right: 0, bottom: 0, opacity: 0.5 },
  button: {
    position: "absolute",
    bottom: 40,
    alignSelf: "center",
    backgroundColor: "#0f172a",
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 6,
  },
});
