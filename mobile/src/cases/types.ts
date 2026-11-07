// Cases domain types

export interface CaseSummary {
  id: string;
  title: string;
  status: string;
  created_at: string;
  match_count?: number;
}

export interface CaseFilters {
  status?: string;
  role?: string;
  page?: number;
  page_size?: number;
}
