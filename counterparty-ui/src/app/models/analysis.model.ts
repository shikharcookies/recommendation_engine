export interface CounterpartyInput {
  name: string;
  country?: string;
  sector?: string;
  intrinsic_hrc?: number;
  intrinsic_pd?: number;
  counterparty_hrc?: number;
  counterparty_pd?: number;
}

export interface AnalysisInput {
  analysis_text?: string;
  pdf_file?: File;
  docx_file?: File;
}

export interface StructuredAnalysis {
  company_profile: string;
  assets: string;
  liquidity: string;
  strategy: string;
  means: string;
  performance: string;
}

export interface RiskSignal {
  signal_type: string;
  value: number;
  unit: string;
  context: string;
}

export interface Scores {
  asset_quality: number;
  liquidity: number;
  capitalisation: number;
  profitability: number;
}

export interface AnalysisResponse {
  analysis_id: string;
  structured_analysis: StructuredAnalysis;
  structured_analysis_bullets?: { [key: string]: string[] };
  signals: RiskSignal[];
  scores: Scores;
  memo: string;
}
