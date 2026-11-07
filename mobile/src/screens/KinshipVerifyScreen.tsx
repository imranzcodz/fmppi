import React from "react";
import { View, Text, StyleSheet, TouchableOpacity, ActivityIndicator, Image } from "react-native";
import * as ImagePicker from "expo-image-picker";
import { api } from "../api/client";

const pickPhoto = async () => {
  const result = await ImagePicker.launchImageLibraryAsync({
    mediaTypes: ImagePicker.MediaTypeOptions.Images,
    allowsEditing: true,
    aspect: [4, 3],
  });
  if (!result.canceled && result.assets[0]) {
    return result.assets[0].uri;
  }
  return null;
};

export default function KinshipVerifyScreen() {
  const [photo1, setPhoto1] = React.useState<string | null>(null);
  const [photo2, setPhoto2] = React.useState<string | null>(null);
  const [submitting, setSubmitting] = React.useState(false);
  const [result, setResult] = React.useState<{ kinScore: number; confidence: number } | null>(null);

  const handlePick = async (slot: 1 | 2) => {
    const uri = await pickPhoto();
    if (uri) {
      slot === 1 ? setPhoto1(uri) : setPhoto2(uri);
    }
  };

  const handleSubmit = async () => {
    if (!photo1 || !photo2) return;
    setSubmitting(true);
    try {
      const form = new FormData();
      const add = (uri: string, key: string) => {
        form.append(key, {
          uri,
          type: "image/jpeg",
          name: `${key}.jpg`,
        } as any);
      };
      add(photo1, "photo1");
      add(photo2, "photo2");
      const { data } = await api.postForm<{ kin_score: number; confidence: number }>(
        "/verify/kinship",
        form
      );
      setResult({ kinScore: data.kin_score, confidence: data.confidence });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Kinship Verify</Text>
      <View style={styles.pair}>
        <View style={styles.photoSlot}>
          <TouchableOpacity style={styles.slot} onPress={() => handlePick(1)}>
            {photo1 ? <Image uri={photo1} /> : <Text>Photo 1</Text>}
          </TouchableOpacity>
        </View>
        <View style={styles.photoSlot}>
          <TouchableOpacity style={styles.slot} onPress={() => handlePick(2)}>
            {photo2 ? <Image uri={photo2} /> : <Text>Photo 2</Text>}
          </TouchableOpacity>
        </View>
      </View>
      {result && (
        <Text style={styles.score}>Kin score: {result.kinScore.toFixed(2)} &bull; Confidence: {(result.confidence * 100).toFixed(1)}%</Text>
      )}
      <TouchableOpacity style={styles.button} onPress={handleSubmit} disabled={submitting || !photo1 || !photo2}>
        <Text>{submitting ? "Scoring..." : "Score Kin Relationship"}</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 16, backgroundColor: "#fff" },
  title: { fontSize: 20, fontWeight: "700", marginBottom: 16 },
  pair: { flexDirection: "row", gap: 12, marginBottom: 16 },
  photoSlot: { flex: 1 },
  slot: { aspectRatio: 1, borderWidth: 1, borderColor: "#ccc", alignItems: "center", justifyContent: "center" },
  score: { fontSize: 16, marginBottom: 16 },
  button: { backgroundColor: "#0f172a", paddingVertical: 12, alignItems: "center", borderRadius: 6 },
});
