"""Profile packager for persisting distilled themes to profiles/ directory."""
import os
import yaml
from slidecraft.ir.theme_schema import ThemeSchema


class ProfilePackager:
    """Saves ThemeSchema and StyleDNA into a standardized profile folder."""
    
    @classmethod
    def save_profile(cls, theme: ThemeSchema, base_dir: str = "profiles") -> str:
        profile_dir = os.path.join(base_dir, theme.profile_name)
        os.makedirs(os.path.join(profile_dir, "components"), exist_ok=True)
        os.makedirs(os.path.join(profile_dir, "raw_samples"), exist_ok=True)
        
        theme_path = os.path.join(profile_dir, "theme.yaml")
        theme_data = theme.model_dump()
        
        with open(theme_path, "w", encoding="utf-8") as f:
            yaml.dump(theme_data, f, sort_keys=False, allow_unicode=True)
            
        return profile_dir
