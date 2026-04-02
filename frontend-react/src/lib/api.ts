import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 60000,
});

export const defaultCustomerPayload = {
  customer_id: "demo-user-001",
  gender: "Female",
  SeniorCitizen: 0,
  Partner: "Yes",
  Dependents: "No",
  tenure: 12,
  PhoneService: "Yes",
  MultipleLines: "No",
  InternetService: "Fiber optic",
  OnlineSecurity: "No",
  OnlineBackup: "Yes",
  DeviceProtection: "No",
  TechSupport: "No",
  StreamingTV: "Yes",
  StreamingMovies: "Yes",
  Contract: "Month-to-month",
  PaperlessBilling: "Yes",
  PaymentMethod: "Electronic check",
  MonthlyCharges: 79.9,
  TotalCharges: 959.0,
  days_since_last_login: 18,
  avg_logins_per_week: 2.1,
  avg_session_duration_minutes: 14.0,
  feature_usage_score: 42.0,
  payment_failures_90d: 1,
  activity_trend_pct: null,
  support_tickets_30d: 0,
};

export const getInsights = async () => {
  const res = await api.get('/insights');
  return res.data;
};

export const getModelMetrics = async () => {
  const res = await api.get('/model-metrics');
  return res.data;
};

export const predictUser = async (payload: any) => {
  const res = await api.post('/predict', payload);
  return res.data;
};

export const simulateUser = async (baseUser: any, updatedUser: any) => {
  const res = await api.post('/simulate', { base_user: baseUser, updated_user: updatedUser });
  return res.data;
};

export const batchPredictUpload = async (file: File, sendEmails = true, dryRun = false, includeEnriched = true) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('send_emails', String(sendEmails));
  formData.append('dry_run', String(dryRun));
  formData.append('include_enriched_csv', String(includeEnriched));

  // Try standard route then fallback if 404
  try {
    const res = await api.post('/batch-predict', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return res.data;
  } catch (err: any) {
    if (err.response?.status === 404) {
      const resFallback = await api.post('/api/batch-predict', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      return resFallback.data;
    }
    throw err;
  }
};
