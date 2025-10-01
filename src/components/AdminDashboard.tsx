import { useState, useEffect } from 'react';
import { LogOut, Download, Trash2, Eye, ChevronLeft, ChevronRight } from 'lucide-react';
import { getAllResumes, downloadResumeAsAdmin, deleteResume, getResumeById, adminLogout } from '../api';
import { ResumeListItem, ResumeData } from '../types';

interface AdminDashboardProps {
  sessionToken: string;
  onLogout: () => void;
}

export default function AdminDashboard({ sessionToken, onLogout }: AdminDashboardProps) {
  const [resumes, setResumes] = useState<ResumeListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [selectedResume, setSelectedResume] = useState<ResumeData | null>(null);

  const fetchResumes = async () => {
    setLoading(true);
    setError('');

    try {
      const response = await getAllResumes(sessionToken, page, 20);
      setResumes(response.resumes);
      setTotalPages(response.total_pages);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch resumes');
      if (err.status === 401) {
        onLogout();
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchResumes();
  }, [page]);

  const handleDownload = async (resumeId: string, fullName: string) => {
    try {
      await downloadResumeAsAdmin(sessionToken, resumeId, fullName);
    } catch (err: any) {
      setError(err.message || 'Failed to download resume');
    }
  };

  const handleDelete = async (resumeId: string) => {
    if (!confirm('Are you sure you want to delete this resume?')) {
      return;
    }

    try {
      await deleteResume(sessionToken, resumeId);
      fetchResumes();
    } catch (err: any) {
      setError(err.message || 'Failed to delete resume');
    }
  };

  const handleView = async (resumeId: string) => {
    try {
      const resume = await getResumeById(sessionToken, resumeId);
      setSelectedResume(resume);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch resume details');
    }
  };

  const handleLogout = async () => {
    try {
      await adminLogout(sessionToken);
    } catch (err) {
      console.error('Logout error:', err);
    } finally {
      onLogout();
    }
  };

  if (selectedResume) {
    return (
      <div className="min-h-screen bg-gray-100 p-6">
        <div className="max-w-4xl mx-auto">
          <button
            onClick={() => setSelectedResume(null)}
            className="mb-4 flex items-center gap-2 text-blue-600 hover:text-blue-800"
          >
            <ChevronLeft className="w-4 h-4" />
            Back to Dashboard
          </button>

          <div className="bg-white rounded-lg shadow-lg p-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">{selectedResume.full_name}</h2>

            <div className="space-y-6">
              <section>
                <h3 className="text-lg font-semibold text-gray-800 mb-2">Contact Information</h3>
                <p className="text-gray-700">Email: {selectedResume.user_email}</p>
                {selectedResume.phone && <p className="text-gray-700">Phone: {selectedResume.phone}</p>}
              </section>

              {Object.keys(selectedResume.social_links).length > 0 && (
                <section>
                  <h3 className="text-lg font-semibold text-gray-800 mb-2">Social Links</h3>
                  {Object.entries(selectedResume.social_links).map(([platform, url]) => (
                    url && (
                      <p key={platform} className="text-gray-700">
                        {platform}: <a href={url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">{url}</a>
                      </p>
                    )
                  ))}
                </section>
              )}

              {selectedResume.profile_summary && (
                <section>
                  <h3 className="text-lg font-semibold text-gray-800 mb-2">Profile Summary</h3>
                  <p className="text-gray-700">{selectedResume.profile_summary}</p>
                </section>
              )}

              {selectedResume.education.length > 0 && (
                <section>
                  <h3 className="text-lg font-semibold text-gray-800 mb-2">Education</h3>
                  {selectedResume.education.map((edu, index) => (
                    <div key={index} className="mb-3">
                      <p className="font-medium text-gray-800">{edu.degree}</p>
                      <p className="text-gray-700">{edu.institution} - {edu.year}</p>
                      {edu.gpa && <p className="text-gray-600">GPA: {edu.gpa}</p>}
                    </div>
                  ))}
                </section>
              )}

              {Object.keys(selectedResume.technical_skills).length > 0 && (
                <section>
                  <h3 className="text-lg font-semibold text-gray-800 mb-2">Technical Skills</h3>
                  {Object.entries(selectedResume.technical_skills).map(([category, skills]) => (
                    <p key={category} className="text-gray-700 mb-1">
                      <span className="font-medium">{category}:</span> {Array.isArray(skills) ? skills.join(', ') : skills}
                    </p>
                  ))}
                </section>
              )}

              {selectedResume.work_experience.length > 0 && (
                <section>
                  <h3 className="text-lg font-semibold text-gray-800 mb-2">Work Experience</h3>
                  {selectedResume.work_experience.map((work, index) => (
                    <div key={index} className="mb-4">
                      <p className="font-medium text-gray-800">{work.title} - {work.company}</p>
                      <p className="text-gray-600 text-sm mb-1">{work.period}</p>
                      <p className="text-gray-700">{work.description}</p>
                    </div>
                  ))}
                </section>
              )}

              {selectedResume.projects.length > 0 && (
                <section>
                  <h3 className="text-lg font-semibold text-gray-800 mb-2">Projects</h3>
                  {selectedResume.projects.map((project, index) => (
                    <div key={index} className="mb-3">
                      <p className="font-medium text-gray-800">{project.name}</p>
                      <p className="text-gray-600 text-sm mb-1">{project.technologies}</p>
                      <p className="text-gray-700">{project.description}</p>
                    </div>
                  ))}
                </section>
              )}

              {selectedResume.languages.length > 0 && (
                <section>
                  <h3 className="text-lg font-semibold text-gray-800 mb-2">Languages</h3>
                  <p className="text-gray-700">
                    {selectedResume.languages.map(lang => `${lang.language} (${lang.proficiency})`).join(', ')}
                  </p>
                </section>
              )}

              {selectedResume.certifications.length > 0 && (
                <section>
                  <h3 className="text-lg font-semibold text-gray-800 mb-2">Certifications</h3>
                  {selectedResume.certifications.map((cert, index) => (
                    <p key={index} className="text-gray-700">
                      {cert.name} - {cert.issuer} ({cert.year})
                    </p>
                  ))}
                </section>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <div className="flex justify-between items-center">
            <h1 className="text-2xl font-bold text-gray-900">Resume Dashboard</h1>
            <button
              onClick={handleLogout}
              className="flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
            >
              <LogOut className="w-4 h-4" />
              Logout
            </button>
          </div>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-700">{error}</p>
          </div>
        )}

        {loading ? (
          <div className="bg-white rounded-lg shadow-lg p-12 text-center">
            <p className="text-gray-600">Loading resumes...</p>
          </div>
        ) : resumes.length === 0 ? (
          <div className="bg-white rounded-lg shadow-lg p-12 text-center">
            <p className="text-gray-600">No resumes found</p>
          </div>
        ) : (
          <>
            <div className="bg-white rounded-lg shadow-lg overflow-hidden">
              <table className="w-full">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Name
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Email
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Phone
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Submitted
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {resumes.map((resume) => (
                    <tr key={resume.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {resume.full_name}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                        {resume.user_email}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                        {resume.phone || '-'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                        {new Date(resume.created_at).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <div className="flex justify-end gap-2">
                          <button
                            onClick={() => handleView(resume.id)}
                            className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                            title="View"
                          >
                            <Eye className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => handleDownload(resume.id, resume.full_name)}
                            className="p-2 text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                            title="Download PDF"
                          >
                            <Download className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => handleDelete(resume.id)}
                            className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                            title="Delete"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {totalPages > 1 && (
              <div className="mt-6 flex justify-center items-center gap-4">
                <button
                  onClick={() => setPage(p => Math.max(1, p - 1))}
                  disabled={page === 1}
                  className="flex items-center gap-2 px-4 py-2 bg-white text-gray-700 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed shadow"
                >
                  <ChevronLeft className="w-4 h-4" />
                  Previous
                </button>

                <span className="text-gray-700">
                  Page {page} of {totalPages}
                </span>

                <button
                  onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                  disabled={page === totalPages}
                  className="flex items-center gap-2 px-4 py-2 bg-white text-gray-700 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed shadow"
                >
                  Next
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
