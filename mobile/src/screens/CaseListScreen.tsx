import React from "react";
import { View, Text, FlatList, TouchableOpacity, StyleSheet, ActivityIndicator } from "react-native";
import { Case } from "../api/types";
import { api } from "../api/client";

export default function CaseListScreen() {
  const [cases, setCases] = React.useState<Case[]>([]);
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    api.get<{ items: Case[] }>("/cases").then(({ data }) => {
      setCases(data.items);
      setLoading(false);
    });
  }, []);

  const renderItem = ({ item }: { item: Case }) => (
    <TouchableOpacity style={styles.row} onPress={() => {}}>
      <Text style={styles.title}>{item.title}</Text>
      <Text style={styles.meta}>{item.status} &bull; {item.created_at}</Text>
    </TouchableOpacity>
  );

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Cases</Text>
      {loading ? (
        <ActivityIndicator size="small" />
      ) : (
        <FlatList
          data={cases}
          renderItem={renderItem}
          keyExtractor={(item) => item.id}
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 16, backgroundColor: "#fff" },
  title: { fontSize: 20, fontWeight: "700", marginBottom: 16 },
  row: { paddingVertical: 12, borderBottomWidth: 1, borderBottomColor: "#eee" },
  titleText: { fontWeight: "600" },
  meta: { fontSize: 12, color: "#666" },
});
