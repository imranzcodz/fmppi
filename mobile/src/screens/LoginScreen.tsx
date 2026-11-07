import React from "react";
import { View, Text, Button, TextInput, StyleSheet, ActivityIndicator } from "react-native";
import { authService } from "../api/client";

export default function LoginScreen() {
  const [email, setEmail] = React.useState("");
  const [password, setPassword] = React.useState("");
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState("");

  const handleLogin = async () => {
    setLoading(true);
    setError("");
    try {
      await authService.login(email, password);
    } catch (err: any) {
      setError(err?.response?.data?.detail ?? "Login failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>FMPPI Mobile</Text>
      <Text style={styles.subtitle}>Field Investigator Login</Text>

      <TextInput
        style={styles.input}
        placeholder="Email"
        value={email}
        onChangeText={setEmail}
        autoCapitalize="none"
      />
      <TextInput
        style={styles.input}
        placeholder="Password"
        value={password}
        onChangeText={setPassword}
        secureTextEntry
      />

      {error && <Text style={styles.error}>{error}</Text>}

      <Button title={loading ? "Signing in..." : "Login"} onPress={handleLogin} disabled={loading} />

      {loading && <ActivityIndicator size="small" style={styles.spinner} />}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: "center", padding: 24, backgroundColor: "#fff" },
  title: { fontSize: 24, fontWeight: "700", marginBottom: 8 },
  subtitle: { fontSize: 14, color: "#666", marginBottom: 24 },
  input: { borderWidth: 1, borderColor: "#ccc", padding: 10, marginBottom: 12, borderRadius: 6 },
  error: { color: "#b00020", marginBottom: 12, fontSize: 13 },
  spinner: { marginTop: 12 },
});
