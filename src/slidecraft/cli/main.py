"""Slidecraft Unified CLI Entrypoint."""
import os
import sys
import argparse
import yaml

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from slidecraft.ir.deck import DeckSchema
from slidecraft.ir.theme_schema import ThemeSchema
from slidecraft.compile.pptx_backend import PPTXBackend
from slidecraft.validate.cognitive_auditor import CognitiveAuditor
from slidecraft.validate.contrast_checker import ContrastChecker
from slidecraft.distill.pptx_decompiler import PPTXDecompiler
from slidecraft.distill.profile_packager import ProfilePackager


def load_theme(profile_name: str, profiles_root: str = "profiles") -> ThemeSchema:
    """Load ThemeSchema from YAML file in profiles directory."""
    theme_path = os.path.join(profiles_root, profile_name, "theme.yaml")
    if not os.path.exists(theme_path):
        # Fallback to academic_light
        theme_path = os.path.join(profiles_root, "academic_light", "theme.yaml")
    
    if os.path.exists(theme_path):
        with open(theme_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            return ThemeSchema(**data)
    return ThemeSchema(profile_name=profile_name)


def load_deck(deck_path: str) -> DeckSchema:
    """Load Canonical DeckSchema from YAML or JSON."""
    with open(deck_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
        return DeckSchema(**data)


def cmd_build(args):
    """Build PPTX from Canonical Deck YAML."""
    print(f"[Slidecraft] Loading deck: {args.deck}")
    deck = load_deck(args.deck)
    profile_name = args.profile or deck.profile_name
    print(f"[Slidecraft] Applying design profile: '{profile_name}'")
    theme = load_theme(profile_name)
    
    # Audit first
    print("\n--- Running Pedagogy & Cognitive Load Audit ---")
    report = CognitiveAuditor.generate_report(deck)
    print(report)
    
    # Compile PPTX
    backend = PPTXBackend(theme)
    out_path = args.output or "output.pptx"
    backend.compile_deck(deck, out_path)
    print(f"[Slidecraft] Successfully compiled presentation: {os.path.abspath(out_path)}")


def cmd_distill(args):
    """Distill theme and layout from a sample file."""
    print(f"[Slidecraft] Distilling from sample: {args.input}")
    if args.input.endswith(".pptx"):
        theme = PPTXDecompiler.inspect(args.input, profile_name=args.name)
        saved_dir = ProfilePackager.save_profile(theme)
        print(f"[Slidecraft] Successfully extracted and created profile in: {saved_dir}")
    else:
        print("[Slidecraft] Creating template profile...")
        theme = ThemeSchema(profile_name=args.name, description=f"Distilled from {args.input}")
        saved_dir = ProfilePackager.save_profile(theme)
        print(f"[Slidecraft] Created base profile in: {saved_dir}")


def cmd_audit(args):
    """Audit deck content without building PPTX."""
    deck = load_deck(args.deck)
    report = CognitiveAuditor.generate_report(deck)
    print(report)


def main():
    parser = argparse.ArgumentParser(prog="slidecraft", description="AI-Agent Presentation & Infographic Engine")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Build command
    parser_build = subparsers.add_parser("build", help="Compile Canonical deck.yaml to PowerPoint PPTX")
    parser_build.add_argument("--deck", "-d", required=True, help="Path to deck.yaml specification")
    parser_build.add_argument("--output", "-o", default="output.pptx", help="Output .pptx path")
    parser_build.add_argument("--profile", "-p", default=None, help="Override profile theme name")
    parser_build.set_defaults(func=cmd_build)

    # Distill command
    parser_distill = subparsers.add_parser("distill", help="Reverse engineer a sample .pptx or image into a profile")
    parser_distill.add_argument("--input", "-i", required=True, help="Path to sample .pptx or image")
    parser_distill.add_argument("--name", "-n", required=True, help="Unique name for the new profile")
    parser_distill.set_defaults(func=cmd_distill)

    # Audit command
    parser_audit = subparsers.add_parser("audit", help="Audit pedagogical compliance and cognitive load")
    parser_audit.add_argument("--deck", "-d", required=True, help="Path to deck.yaml specification")
    parser_audit.set_defaults(func=cmd_audit)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
