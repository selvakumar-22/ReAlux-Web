import api from './client';


// ============================================================
// TYPES
// ============================================================

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  name: string;
  email: string;
  password: string;
}

export interface User {
  id: number;
  name: string;
  email: string;
}

export interface AnalysisRunRequest {
  sample_id: string;
  sample_type: string;
  source: string;
  test_method: string;
  input_method: string;
  composition: Record<string, number>;
}

export interface AnalysisResult {
  analysis_id: number;
  metal_recovery: number;
  alumina_recovery: number;
  recovery_category: string;
  best_method: string;
  method_reason: string;
  model_used: string;
  model_type: string;
  sufficient_data: boolean;
  n_samples: number;

  r2_metal?: number;
  mae_metal?: number;
  rmse_metal?: number;

  r2_alumina?: number;
  mae_alumina?: number;
  rmse_alumina?: number;

  safety_summary: any;

  industrial_apps: string[];
  environmental_benefits: string[];

  composition: Record<string, number>;

  sds_sections?: any;
  sds_product_name?: string;
}


// ============================================================
// AUTH
// ============================================================

export const auth = {

  login: async (data: LoginRequest) => {
    const response = await api.post('/auth/login', data);

    // Save access token automatically after successful login
    const token = response.data?.access_token;

    if (token) {
      localStorage.setItem('access_token', token);
      console.log('Login successful. Access token saved.');
    } else {
      console.warn('Login response did not contain access_token.');
    }

    return response;
  },

  register: async (data: RegisterRequest) => {
    const response = await api.post('/auth/register', data);

    // Some backends return token immediately after registration
    const token = response.data?.access_token;

    if (token) {
      localStorage.setItem('access_token', token);
      console.log('Registration successful. Access token saved.');
    }

    return response;
  },

  me: () => {
    return api.get<User>('/auth/me');
  },

  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');

    console.log('Logged out.');
  },
};


// ============================================================
// ANALYSIS
// ============================================================

export const analysis = {

  uploadFile: (file: File) => {
    const formData = new FormData();

    formData.append('file', file);

    return api.post('/analysis/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },

  run: (data: AnalysisRunRequest) => {
    return api.post<AnalysisResult>('/analysis/run', data);
  },

  history: () => {
    return api.get('/analysis/history');
  },

  get: (id: number) => {
    return api.get(`/analysis/${id}`);
  },
};


// ============================================================
// REPORTS
// ============================================================

export const reports = {

  generate: (analysisId: number) => {
    return api.post(
      `/reports/generate?analysis_id=${analysisId}`
    );
  },

  download: (reportId: number) => {
    return api.get(
      `/reports/download/${reportId}`,
      {
        responseType: 'blob',
      }
    );
  },

  history: () => {
    return api.get('/reports/history');
  },
};


// ============================================================
// DATASET
// ============================================================

export const dataset = {

  // Notice the trailing slash
  get: () => {
    return api.get('/dataset/');
  },

  upload: (file: File) => {
    const formData = new FormData();

    formData.append('file', file);

    return api.post('/dataset/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
};