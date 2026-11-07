import { createNativeStackNavigator } from "@react-navigation/native-stack";
import { NavigationContainer } from "@react-navigation/native";
import React from "react";

import LoginScreen from "../screens/LoginScreen";
import CaseListScreen from "../screens/CaseListScreen";
import CaseDetailScreen from "../screens/CaseDetailScreen";
import LocalVerifyScreen from "../screens/LocalVerifyScreen";
import KinshipVerifyScreen from "../screens/KinshipVerifyScreen";

const Stack = createNativeStackNavigator();

export type RootStackParamList = {
  Login: undefined;
  CaseList: undefined;
  CaseDetail: { caseId: string };
  LocalVerify: undefined;
  KinshipVerify: undefined;
};

export default function AppNavigator() {
  return (
    <NavigationContainer>
      <Stack.Navigator
        screenOptions={{
          headerTintColor: "#fff",
          headerStyle: { backgroundColor: "#0f172a" },
        }}
      >
        <Stack.Screen
          name="Login"
          component={LoginScreen}
          options={{ headerShown: false }}
        />
        <Stack.Screen name="CaseList" component={CaseListScreen} />
        <Stack.Screen name="CaseDetail" component={CaseDetailScreen} />
        <Stack.Screen name="LocalVerify" component={LocalVerifyScreen} />
        <Stack.Screen name="KinshipVerify" component={KinshipVerifyScreen} />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
