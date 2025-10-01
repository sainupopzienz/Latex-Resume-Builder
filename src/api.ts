import { ResumeData } from './types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'ApiError';
  }
}

async function handleResponse(response: Response) {
  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: 'An error occurred' }));
    throw new ApiError(response.status, error.error || error.message || 'An error occurred');
  }
  return response.json();
}

export async function submitResume(data: ResumeData) {
  const response = await fetch(`${API_BASE_URL}/resumes`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });
  return handleResponse(response);
}

export async function downloadResumePDF(resumeId: string) {
  const response = await fetch(`${API_BASE_URL}/resumes/${resumeId}/pdf`);

  if (!response.ok) {
    throw new ApiError(response.status, 'Failed to download PDF');
  }

  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `resume_${resumeId}.pdf`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  window.URL.revokeObjectURL(url);
}

export async function adminLogin(email: string, password: string) {
  const response = await fetch(`${API_BASE_URL}/admin/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ email, password }),
  });
  return handleResponse(response);
}

export async function adminLogout(sessionToken: string) {
  const response = await fetch(`${API_BASE_URL}/admin/logout`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${sessionToken}`,
    },
  });
  return handleResponse(response);
}

export async function getAllResumes(sessionToken: string, page = 1, perPage = 20) {
  const response = await fetch(`${API_BASE_URL}/admin/resumes?page=${page}&per_page=${perPage}`, {
    headers: {
      'Authorization': `Bearer ${sessionToken}`,
    },
  });
  return handleResponse(response);
}

export async function getResumeById(sessionToken: string, resumeId: string) {
  const response = await fetch(`${API_BASE_URL}/admin/resumes/${resumeId}`, {
    headers: {
      'Authorization': `Bearer ${sessionToken}`,
    },
  });
  return handleResponse(response);
}

export async function downloadResumeAsAdmin(sessionToken: string, resumeId: string, fullName: string) {
  const response = await fetch(`${API_BASE_URL}/admin/resumes/${resumeId}/pdf`, {
    headers: {
      'Authorization': `Bearer ${sessionToken}`,
    },
  });

  if (!response.ok) {
    throw new ApiError(response.status, 'Failed to download PDF');
  }

  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `${fullName.replace(/\s+/g, '_')}_resume.pdf`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  window.URL.revokeObjectURL(url);
}

export async function deleteResume(sessionToken: string, resumeId: string) {
  const response = await fetch(`${API_BASE_URL}/admin/resumes/${resumeId}`, {
    method: 'DELETE',
    headers: {
      'Authorization': `Bearer ${sessionToken}`,
    },
  });
  return handleResponse(response);
}
