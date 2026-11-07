// Biometric consent prompt (expo-local-authentication)

import * as LocalAuthentication from "expo-local-authentication";

export interface BiometricResult {
  success: boolean;
  type: LocalAuthentication.AuthenticationType | null;
  error: string | null;
}

export async function isBiometricAvailable(): Promise<boolean> {
  const { available } = await LocalAuthentication.hasHardwareAsync();
  if (!available) return false;
  const enrolled = await LocalAuthentication.isEnrolledAsync();
  return enrolled;
}

export async function promptBiometricConsent(
  reason = "Authenticate to capture a probe photo for verification."
): Promise<BiometricResult> {
  try {
    const available = await isBiometricAvailable();
    if (!available) {
      return { success: false, type: null, error: "Biometrics not available or not enrolled." };
    }

    const result = await LocalAuthentication.authenticateAsync({
      promptMessage: reason,
      cancelLabel: "Cancel",
      fallbackLabel: "Use passcode",
    });

    if (result.success) {
      return {
        success: true,
        type: result.type ?? null,
        error: null,
      };
    }

    return {
      success: false,
      type: result.type ?? null,
      error: "Biometric authentication was cancelled or failed.",
    };
  } catch (err: any) {
    return {
      success: false,
      type: null,
      error: err?.message ?? "Biometric prompt error.",
    };
  }
}
