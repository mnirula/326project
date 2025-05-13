from typing import List


# Base class for a resume section
class Section:
    def __init__(self, title: str, content: str = ""):
        self.title = title              # Name of the section (e.g., Experience, Skills)
        self.content = content          # Text content of the section


    def __repr__(self):
        # Helpful string representation showing title and content length
        return f"<Section {self.title}: {len(self.content)} chars>"


# Specialized section classes inheriting from Section


class ExperienceSection(Section):
    def __init__(self, content: str = ""):
        super().__init__("Experience", content)


class EducationSection(Section):
    def __init__(self, content: str = ""):
        super().__init__("Education", content)


class SkillsSection(Section):
    def __init__(self, content: str = ""):
        super().__init__("Skills", content)


class ProjectsSection(Section):
    def __init__(self, content: str = ""):
        super().__init__("Projects", content)


# Resume class holding multiple sections
class Resume:
    def __init__(self):
        # Initialize empty content sections (to be filled during parsing)
        self.experience = ExperienceSection()
        self.education = EducationSection()
        self.skills = SkillsSection()
        self.projects = ProjectsSection()


    def all_text(self) -> str:
        # Combine the content of all sections into one string for analysis
        return " ".join([
            self.experience.content or "",
            self.education.content or "",
            self.skills.content or "",
            self.projects.content or ""
        ])





