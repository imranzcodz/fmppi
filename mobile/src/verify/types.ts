// Verify domain types (local-verify + kinship-verify)

export interface LocalVerifyForm {
  probePhotoUri: string;
  topK?: number;
  minSimilarity?: number;
}

export interface LocalVerifyResult {
  queryId: string;
  matches: MatchResultView[];
}

export interface MatchResultView {
  caseId: string;
  personId?: string;
  similarity: number;
  thumbnailUrl?: string;
  caseTitle?: string;
}

export interface KinshipVerifyForm {
  photo1Uri: string;
  photo2Uri: string;
}

export interface KinshipVerifyResult {
  pairId: string;
  kinScore: number;
  confidence: number;
  related: boolean;
}
