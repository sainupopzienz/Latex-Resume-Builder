export interface SocialLinks {
  linkedin?: string;
  github?: string;
  portfolio?: string;
  [key: string]: string | undefined;
}

export interface Education {
  degree: string;
  institution: string;
  year: string;
  gpa?: string;
}

export interface TechnicalSkills {
  [category: string]: string[];
}

export interface WorkExperience {
  title: string;
  company: string;
  period: string;
  description: string;
}

export interface Project {
  name: string;
  description: string;
  technologies: string;
}

export interface Language {
  language: string;
  proficiency: string;
}

export interface Certification {
  name: string;
  issuer: string;
  year: string;
}

export interface ResumeData {
  full_name: string;
  user_email: string;
  phone: string;
  social_links: SocialLinks;
  profile_summary: string;
  education: Education[];
  technical_skills: TechnicalSkills;
  work_experience: WorkExperience[];
  projects: Project[];
  languages: Language[];
  certifications: Certification[];
}

export interface ResumeListItem {
  id: string;
  user_email: string;
  full_name: string;
  phone: string;
  created_at: string;
  updated_at: string;
}
