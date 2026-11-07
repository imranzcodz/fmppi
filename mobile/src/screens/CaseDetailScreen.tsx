import React from "react";
import { View, Text, StyleSheet, ActivityIndicator } from "react-native";
import { RouteProp, useRoute } from "@react-navigation/native";
import { RootStackParamList } from "../navigation/AppNavigator";
import { CaseDetail } from "../api/types";
import { api } from "../api/client";

type CaseDetailRoute = RouteProp<RootStackParamList, "CaseDetail">;

export default function CaseDetailScreen() {
  const route = useRoute<CaseDetailRoute>();
  const { caseId } = route.params;
  const [casedetail, setCase] = React.useState<CaseDetail | null>(null);
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    api.get<CaseDetail>(`/cases/${caseId}`).then(({ data }) => {
      setCase(data);
      setLoading(false);
    });
  }, [caseId]);

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Case Detail</Text>
      {loading ? (
        <ActivityIndicator size="small" />
      ) : casedetail ? (
        <View>
          <Text style={styles.field}>{casedetail.title}</Text>
          <Text style={styles.meta}>Status: {casedetail.status}</Text>
          <Text style={styles.meta}>Matches: {casedetail.match_count ?? 0}</Text>
        </View>
      ) : null}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 16, backgroundColor: "#fff" },
  title: { fontSize: 20, fontWeight: "700", marginBottom: 16 },
  field: { fontSize: 16, marginBottom: 6 },
  meta: { fontSize: 13, color: "#666", marginBottom: 4 },
});
