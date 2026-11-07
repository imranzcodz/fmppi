// Offline capture queue types (sync on reconnect)

export type QueueItemStatus = "pending" | "uploading" | "synced" | "failed";

export interface QueuedCapture {
  id: string;
  type: "local-verify" | "kinship-verify" | "evidence";
  payload: unknown;
  createdAt: string;
  status: QueueItemStatus;
  attempts: number;
  error?: string;
}

export interface QueueState {
  items: QueuedCapture[];
  isSyncing: boolean;
  lastSyncedAt: string | null;
}
