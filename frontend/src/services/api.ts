import type {
  SystemHealth,
  VerificationReport,
  CorrectionResponse,
  DocumentItem,
  DocumentChunk,
  EvaluationExperiment,
  ClaimResult,
  HaluEvalStatus,
  EvaluationPrediction,
  MultiModelComparisonResponse
} from '../types';

const getBaseUrl = (): string => {
  const envUrl = import.meta.env.VITE_API_BASE_URL;
  if (envUrl && typeof envUrl === 'string' && envUrl.trim()) {
    return envUrl.trim().replace(/\/+$/, '');
  }
  // Default to relative '/api/v1' to leverage Vite dev proxy / reverse proxy,
  // preventing hardcoded port collisions and CORS issues.
  return '/api/v1';
};

const BASE_URL = getBaseUrl();

async function handleResponse<T>(res: Response, endpointUrl?: string): Promise<T> {
  if (!res.ok) {
    let detail = '';
    try {
      const errorData = await res.json();
      detail = errorData.detail || errorData.message || '';
    } catch {
      detail = res.statusText;
    }

    if (res.status === 404) {
      if (!detail || detail === 'Not Found') {
        throw new Error(
          `TruthGuard API endpoint not found (HTTP 404${endpointUrl ? ` at ${endpointUrl}` : ''}). Please verify the backend is running and the route prefix matches /api/v1.`
        );
      }
      throw new Error(detail);
    }

    if (res.status === 502 || res.status === 503 || res.status === 504) {
      throw new Error(
        `TruthGuard backend service unavailable (HTTP ${res.status}). Please check that the FastAPI server is running.`
      );
    }

    throw new Error(detail || `Request failed with status ${res.status}`);
  }
  return res.json();
}

async function apiFetch(endpoint: string, init?: RequestInit): Promise<Response> {
  const url = `${BASE_URL}${endpoint}`;
  try {
    return await fetch(url, init);
  } catch (err: any) {
    throw new Error(
      `Unable to connect to TruthGuard backend at ${url}. Please verify that the backend server is running.`
    );
  }
}

export const api = {
  // System Health & Models
  async getHealth(): Promise<SystemHealth> {
    const res = await apiFetch('/health');
    return handleResponse<SystemHealth>(res, '/health');
  },

  async getModels(): Promise<{ models: any[]; default_model: string; fallback_model: string }> {
    const res = await apiFetch('/models');
    return handleResponse(res, '/models');
  },

  // LLM Generation
  async generateAnswer(prompt: string, model?: string): Promise<{ response: string }> {
    const res = await apiFetch('/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt, model })
    });
    return handleResponse(res, '/generate');
  },

  // Claim Extraction
  async extractClaims(text: string, context_question?: string): Promise<{ total_claims: number; claims: ClaimResult[] }> {
    const res = await apiFetch('/claims/extract', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, context_question })
    });
    return handleResponse(res, '/claims/extract');
  },

  // Verification
  async verifyAnswer(payload: {
    question: string;
    answer?: string;
    model_name?: string;
    document_ids?: string[];
    evidence_source?: "documents" | "fever" | "both";
    top_k?: number;
    enable_investigation_agent?: boolean;
    enable_multi_model?: boolean;
  }): Promise<VerificationReport> {
    const res = await apiFetch('/verify', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    return handleResponse<VerificationReport>(res, '/verify');
  },

  async getVerifications(): Promise<VerificationReport[]> {
    const res = await apiFetch('/verifications');
    return handleResponse<VerificationReport[]>(res, '/verifications');
  },

  async getVerification(id: string): Promise<VerificationReport> {
    const res = await apiFetch(`/verifications/${id}`);
    return handleResponse<VerificationReport>(res, `/verifications/${id}`);
  },

  // Correction
  async correctResponse(payload: {
    verification_id: string;
    model_name?: string;
    temperature?: number;
  }): Promise<CorrectionResponse> {
    const res = await apiFetch('/correct', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    return handleResponse<CorrectionResponse>(res, '/correct');
  },

  // Documents
  async uploadDocument(file: File): Promise<{ document: DocumentItem; chunks_created: number; message: string }> {
    const formData = new FormData();
    formData.append('file', file);
    const res = await apiFetch('/documents/upload', {
      method: 'POST',
      body: formData
    });
    return handleResponse(res, '/documents/upload');
  },

  async getDocuments(): Promise<{ documents: DocumentItem[]; total_count: number }> {
    const res = await apiFetch('/documents');
    return handleResponse(res, '/documents');
  },

  async getDocumentChunks(id: string): Promise<DocumentChunk[]> {
    const res = await apiFetch(`/documents/${id}/chunks`);
    return handleResponse<DocumentChunk[]>(res, `/documents/${id}/chunks`);
  },

  async deleteDocument(id: string): Promise<{ message: string }> {
    const res = await apiFetch(`/documents/${id}`, {
      method: 'DELETE'
    });
    return handleResponse(res, `/documents/${id}`);
  },

  // Evaluations
  async runEvaluation(payload: {
    benchmark_name: string;
    task?: string;
    sample_size?: number;
    seed?: number;
    sampling_strategy?: string;
    model_name?: string;
    evidence_source?: string;
    split?: string;
    top_k?: number;
  }): Promise<EvaluationExperiment> {
    const res = await apiFetch('/evaluations/run', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    return handleResponse<EvaluationExperiment>(res, '/evaluations/run');
  },

  async compareModels(payload: {
    benchmark_name: string;
    task?: string;
    sample_size?: number;
    seed?: number;
    llm_model?: string;
  }): Promise<MultiModelComparisonResponse> {
    const res = await apiFetch('/evaluations/compare', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    return handleResponse<MultiModelComparisonResponse>(res, '/evaluations/compare');
  },

  async getEvaluations(): Promise<EvaluationExperiment[]> {
    const res = await apiFetch('/evaluations');
    return handleResponse<EvaluationExperiment[]>(res, '/evaluations');
  },

  async getEvaluation(id: string): Promise<EvaluationExperiment> {
    const res = await apiFetch(`/evaluations/${id}`);
    return handleResponse<EvaluationExperiment>(res, `/evaluations/${id}`);
  },

  async getEvaluationPredictions(id: string): Promise<EvaluationPrediction[]> {
    const res = await apiFetch(`/evaluations/${id}/predictions`);
    return handleResponse<EvaluationPrediction[]>(res, `/evaluations/${id}/predictions`);
  },

  // HaluEval Dataset Management
  async getHaluEvalStatus(): Promise<HaluEvalStatus> {
    const res = await apiFetch('/datasets/halueval/status');
    return handleResponse<HaluEvalStatus>(res, '/datasets/halueval/status');
  },

  // FEVER Dataset & Knowledge Base Management
  async getFEVERStatus(): Promise<any> {
    const res = await apiFetch('/datasets/fever/status');
    return handleResponse(res, '/datasets/fever/status');
  },

  async prepareFEVER(payload: {
    split?: string;
    limit?: number;
    seed?: number;
    force_download?: boolean;
  }): Promise<any> {
    const res = await apiFetch('/datasets/fever/prepare', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    return handleResponse(res, '/datasets/fever/prepare');
  },

  async indexFEVER(payload: {
    split?: string;
    limit?: number;
    max_articles?: number;
    rebuild?: boolean;
  }): Promise<any> {
    const res = await apiFetch('/datasets/fever/index', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    return handleResponse(res, '/datasets/fever/index');
  },

  async clearFEVERIndex(): Promise<any> {
    const res = await apiFetch('/datasets/fever/index', {
      method: 'DELETE'
    });
    return handleResponse(res, '/datasets/fever/index');
  }
};

