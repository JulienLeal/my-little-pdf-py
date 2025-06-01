#!/usr/bin/env python3
"""
Command Line Interface for Markdown-to-PDF Converter.

This module provides a user-friendly CLI for converting Markdown documents to
professional PDFs with theme support and advanced features.
"""

import argparse
import logging
import sys
import traceback
from pathlib import Path
from typing import List, Optional, Union

from markdown.extensions import Extension

from .config import ValidationError, load_theme_config
from .core import MarkdownToPDFConverter


class CLIError(Exception):
    """CLI-specific error for user-friendly error handling."""

    def __init__(
        self, message: str, exit_code: int = 1, suggestions: Optional[List[str]] = None
    ):
        """Initialize CLI error.

        Args:
            message: Error message
            exit_code: Exit code to use
            suggestions: Optional list of suggestions to help the user
        """
        self.exit_code = exit_code
        self.suggestions = suggestions or []
        super().__init__(message)


class ValidationErrorCollector:
    """Collects and formats multiple validation errors."""

    def __init__(self):
        self.errors = []
        self.warnings = []

    def add_error(self, message: str, suggestions: Optional[List[str]] = None):
        """Add an error message."""
        self.errors.append({"message": message, "suggestions": suggestions or []})

    def add_warning(self, message: str):
        """Add a warning message."""
        self.warnings.append(message)

    def has_errors(self) -> bool:
        """Check if there are any errors."""
        return len(self.errors) > 0

    def format_errors(self) -> str:
        """Format all errors and suggestions into a user-friendly message."""
        if not self.errors:
            return ""

        parts = ["❌ Validation failed with the following errors:\n"]

        for i, error in enumerate(self.errors, 1):
            parts.append(f"  {i}. {error['message']}")
            if error["suggestions"]:
                for suggestion in error["suggestions"]:
                    parts.append(f"     💡 {suggestion}")
            parts.append("")  # Empty line between errors

        if self.warnings:
            parts.append("⚠️  Warnings:")
            for warning in self.warnings:
                parts.append(f"  • {warning}")
            parts.append("")

        return "\n".join(parts)


class MarkdownToPDFCLI:
    """Command Line Interface for Markdown-to-PDF conversion."""

    def __init__(self):
        self.logger = self._setup_logging()
        self.converter = None

    def _setup_logging(self, level: int = logging.INFO) -> logging.Logger:
        """Set up logging configuration.

        Args:
            level: Logging level

        Returns:
            Configured logger
        """
        logger = logging.getLogger("md_to_pdf")
        logger.setLevel(level)

        # Remove existing handlers to avoid duplicates
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

        # Create console handler
        handler = logging.StreamHandler()
        handler.setLevel(level)

        # Create formatter
        formatter = logging.Formatter("%(message)s")
        handler.setFormatter(formatter)

        logger.addHandler(handler)
        return logger

    def create_parser(self) -> argparse.ArgumentParser:
        """Create command line argument parser.

        Returns:
            Configured ArgumentParser
        """
        parser = argparse.ArgumentParser(
            prog="md-to-pdf",
            description="Convert Markdown documents to professional PDFs",
            epilog="""
Examples:
  %(prog)s document.md                    # Basic conversion
  %(prog)s document.md -o report.pdf      # Specify output file
  %(prog)s document.md -t theme.yaml      # Use custom theme
  %(prog)s document.md --verbose          # Verbose output
  %(prog)s *.md -d output/                # Convert multiple files
            """,
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )

        # Input files
        parser.add_argument(
            "input_files",
            nargs="*",  # Changed from '+' to '*' to allow validation without files
            help="Markdown file(s) to convert (supports glob patterns)",
        )

        # Output options
        output_group = parser.add_argument_group("Output Options")
        output_group.add_argument(
            "-o",
            "--output",
            type=str,
            help="Output PDF file path (for single input) or directory (for multiple inputs)",
        )
        output_group.add_argument(
            "-d",
            "--output-dir",
            type=str,
            help="Output directory for converted PDFs (alternative to --output for multiple files)",
        )

        # Theme and styling
        style_group = parser.add_argument_group("Styling Options")
        style_group.add_argument(
            "-t", "--theme", type=str, help="Theme configuration file (.yaml)"
        )
        style_group.add_argument(
            "--no-theme",
            action="store_true",
            help="Disable theme and use default styling only",
        )
        style_group.add_argument(
            "--css", type=str, help="Additional CSS file to include"
        )

        # Document options
        doc_group = parser.add_argument_group("Document Options")
        doc_group.add_argument(
            "--title", type=str, help="Document title (overrides auto-detected title)"
        )
        doc_group.add_argument("--author", type=str, help="Document author")

        # Processing options
        proc_group = parser.add_argument_group("Processing Options")
        proc_group.add_argument(
            "--extensions",
            type=str,
            nargs="*",
            help="Markdown extensions to enable (default: tables, fenced_code, codehilite)",
        )
        proc_group.add_argument(
            "--no-components",
            action="store_true",
            help="Disable custom component processing",
        )

        # Output control
        control_group = parser.add_argument_group("Output Control")
        control_group.add_argument(
            "-v", "--verbose", action="store_true", help="Verbose output"
        )
        control_group.add_argument(
            "-q", "--quiet", action="store_true", help="Minimal output (errors only)"
        )
        control_group.add_argument(
            "--debug",
            action="store_true",
            help="Debug output with detailed information",
        )
        control_group.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be done without actually converting",
        )

        # Validation and help
        help_group = parser.add_argument_group("Help and Validation")
        help_group.add_argument(
            "--validate",
            action="store_true",
            help="Validate theme file without converting",
        )
        help_group.add_argument(
            "--strict",
            action="store_true",
            help="Enable strict validation mode (treat warnings as errors)",
        )
        help_group.add_argument("--version", action="version", version="%(prog)s 1.0.0")

        return parser

    def _validate_input_files(
        self, input_patterns: List[str], strict: bool = False
    ) -> List[Path]:
        """Validate and expand input file patterns with comprehensive error handling.

        Args:
            input_patterns: List of file patterns or paths
            strict: Whether to enable strict validation mode

        Returns:
            List of existing Markdown files

        Raises:
            CLIError: If validation fails
        """
        if not input_patterns:
            raise CLIError(
                "No input files specified",
                suggestions=[
                    "Provide at least one Markdown file path",
                    "Use glob patterns like '*.md' to process multiple files",
                    "Run with --help to see usage examples",
                ],
            )

        validator = ValidationErrorCollector()
        files = []
        total_patterns_processed = 0

        for pattern in input_patterns:
            total_patterns_processed += 1
            pattern_path = Path(pattern)
            pattern_files = []

            # Handle direct file paths
            if pattern_path.exists() and pattern_path.is_file():
                pattern_files.append(pattern_path)
            elif pattern_path.exists() and pattern_path.is_dir():
                validator.add_error(
                    f"'{pattern}' is a directory, not a file",
                    suggestions=[
                        f"Use '{pattern}/*.md' to convert all Markdown files in the directory",
                        f"Specify a specific file like '{pattern}/document.md'",
                    ],
                )
                continue
            else:
                # Handle glob patterns
                parent = (
                    pattern_path.parent if pattern_path.parent.exists() else Path(".")
                )
                try:
                    matching_files = list(parent.glob(pattern_path.name))
                    if matching_files:
                        pattern_files.extend([f for f in matching_files if f.is_file()])
                    else:
                        # Check if the pattern has wildcards
                        if "*" in pattern or "?" in pattern or "[" in pattern:
                            validator.add_warning(
                                f"No files found matching pattern: {pattern}"
                            )
                        else:
                            validator.add_error(
                                f"File not found: {pattern}",
                                suggestions=[
                                    "Check if the file path is correct",
                                    "Ensure the file has a .md or .markdown extension",
                                    f"Create the file first: touch {pattern}",
                                ],
                            )
                        continue
                except OSError as e:
                    validator.add_error(
                        f"Cannot access path '{pattern}': {e}",
                        suggestions=[
                            "Check file permissions",
                            "Verify the path exists and is accessible",
                        ],
                    )
                    continue

            files.extend(pattern_files)

        # Validate file extensions and readability
        md_extensions = {".md", ".markdown", ".mdown", ".mkd", ".mkdn"}
        valid_files = []

        for file_path in files:
            # Check extension
            if file_path.suffix.lower() not in md_extensions:
                validator.add_error(
                    f"'{file_path}' does not appear to be a Markdown file",
                    suggestions=[
                        f"Supported extensions: {', '.join(sorted(md_extensions))}",
                        "Rename the file with a .md extension if it contains Markdown",
                        "Use --help to see supported file types",
                    ],
                )
                continue

            # Check readability
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    # Try to read first few bytes to ensure it's readable
                    f.read(100)
                valid_files.append(file_path)
            except PermissionError:
                validator.add_error(
                    f"Permission denied reading '{file_path}'",
                    suggestions=[
                        "Check file permissions",
                        f"Try: chmod +r {file_path} (on Unix-like systems)",
                    ],
                )
            except UnicodeDecodeError:
                validator.add_error(
                    f"'{file_path}' is not a valid UTF-8 text file",
                    suggestions=[
                        "Ensure the file is saved with UTF-8 encoding",
                        "Check if this is actually a Markdown file",
                    ],
                )
            except Exception as e:
                validator.add_error(
                    f"Cannot read '{file_path}': {e}",
                    suggestions=[
                        "Check if the file is corrupted or in use by another application"
                    ],
                )

        # Check if no valid files found
        if not valid_files:
            if not validator.has_errors():
                validator.add_error(
                    "No valid Markdown files found",
                    suggestions=[
                        f"Supported extensions: {', '.join(sorted(md_extensions))}",
                        "Check your file paths and try again",
                        "Use 'ls *.md' to see available Markdown files",
                    ],
                )

        # Handle strict mode
        if strict and validator.warnings:
            for warning in validator.warnings:
                validator.add_error(f"Warning (strict mode): {warning}")

        # Raise errors if any
        if validator.has_errors():
            raise CLIError(validator.format_errors())

        # Log warnings in non-strict mode
        for warning in validator.warnings:
            self.logger.warning(f"⚠️  {warning}")

        self.logger.debug(
            f"Validated {len(valid_files)} file(s) from {total_patterns_processed} pattern(s)"
        )
        return valid_files

    def _validate_theme_file(self, theme_path: str, strict: bool = False) -> Path:
        """Validate theme configuration file with enhanced error handling.

        Args:
            theme_path: Path to theme file
            strict: Whether to enable strict validation

        Returns:
            Validated Path object

        Raises:
            CLIError: If theme file is invalid
        """
        path = Path(theme_path)
        validator = ValidationErrorCollector()

        # Basic file existence and type checks
        if not path.exists():
            validator.add_error(
                f"Theme file not found: {theme_path}",
                suggestions=[
                    "Check if the file path is correct",
                    "Ensure the theme file exists",
                    "Use 'ls' to see available files in the directory",
                    "Try using an absolute path",
                ],
            )
        elif not path.is_file():
            validator.add_error(
                f"Theme path is not a file: {theme_path}",
                suggestions=[
                    "Ensure the path points to a file, not a directory",
                    f"Use '{theme_path}/theme.yaml' if it's a directory containing theme files",
                ],
            )
        elif path.suffix.lower() not in {".yaml", ".yml"}:
            validator.add_error(
                f"Theme file must be YAML (.yaml or .yml): {theme_path}",
                suggestions=[
                    "Rename the file with .yaml or .yml extension",
                    "Ensure the file contains YAML configuration",
                    "Check if you meant to specify a different file",
                ],
            )
        else:
            # Validate theme content
            try:
                config = load_theme_config(path, validate_files=False)
                self.logger.debug(f"Theme file validated: {theme_path}")

                # Additional checks in strict mode
                if strict:
                    # Check for potential issues
                    if hasattr(config, "fonts") and config.fonts:
                        validator.add_warning(
                            "Theme references custom fonts - ensure they are available"
                        )

                    if (
                        hasattr(config, "custom_components")
                        and config.custom_components
                    ):
                        component_count = len(config.custom_components)
                        if component_count > 10:
                            validator.add_warning(
                                f"Theme defines {component_count} custom components - this may impact performance"
                            )

            except ValidationError as e:
                validator.add_error(
                    f"Invalid theme configuration: {e.message}",
                    suggestions=[
                        "Check the YAML syntax is correct",
                        "Verify all required fields are present",
                        "Compare with example theme files",
                        "Use 'md-to-pdf --validate --theme your-theme.yaml' to see detailed errors",
                    ],
                )
            except Exception as e:
                validator.add_error(
                    f"Error reading theme file: {e}",
                    suggestions=[
                        "Check file permissions",
                        "Ensure the file is not corrupted",
                        "Verify the file contains valid YAML",
                    ],
                )

        # Handle validation results
        if strict and validator.warnings:
            for warning in validator.warnings:
                validator.add_error(f"Warning (strict mode): {warning}")

        if validator.has_errors():
            raise CLIError(validator.format_errors())

        # Log warnings in non-strict mode
        for warning in validator.warnings:
            self.logger.warning(f"⚠️  {warning}")

        return path

    def _validate_output_options(
        self, args: argparse.Namespace, input_files: List[Path]
    ) -> None:
        """Validate output-related arguments with comprehensive error checking.

        Args:
            args: Parsed command line arguments
            input_files: List of validated input files

        Raises:
            CLIError: If output options are invalid
        """
        validator = ValidationErrorCollector()
        is_single_file = len(input_files) == 1

        # Check for conflicting output options
        if args.output and args.output_dir:
            validator.add_error(
                "Cannot specify both --output and --output-dir",
                suggestions=[
                    "Use --output for single file or specific output path",
                    "Use --output-dir for multiple files output directory",
                ],
            )

        # Validate output path
        if args.output:
            output_path = Path(args.output)

            # For single file
            if is_single_file:
                # Check if output directory exists
                if output_path.parent != Path(".") and not output_path.parent.exists():
                    try:
                        output_path.parent.mkdir(parents=True, exist_ok=True)
                        self.logger.debug(
                            f"Created output directory: {output_path.parent}"
                        )
                    except PermissionError:
                        validator.add_error(
                            f"Cannot create output directory: {output_path.parent}",
                            suggestions=[
                                "Check directory permissions",
                                "Choose a different output location",
                            ],
                        )
                    except Exception as e:
                        validator.add_error(f"Error creating output directory: {e}")

                # Check if output file already exists
                if output_path.exists() and output_path.is_file():
                    validator.add_warning(
                        f"Output file already exists and will be overwritten: {output_path}"
                    )

            # For multiple files
            else:
                if output_path.exists() and output_path.is_file():
                    validator.add_error(
                        f"Cannot use existing file '{args.output}' as output directory for multiple files",
                        suggestions=[
                            "Use --output-dir instead for multiple files",
                            "Choose a directory path for --output",
                            "Process files one at a time with specific output paths",
                        ],
                    )

        # Validate output directory
        if args.output_dir:
            output_dir = Path(args.output_dir)

            # Check if it's an existing file
            if output_dir.exists() and output_dir.is_file():
                validator.add_error(
                    f"Output directory path '{args.output_dir}' is an existing file",
                    suggestions=[
                        "Choose a different directory path",
                        "Remove the existing file if it's not needed",
                    ],
                )

            # Try to create directory
            if not output_dir.exists():
                try:
                    output_dir.mkdir(parents=True, exist_ok=True)
                    self.logger.debug(f"Created output directory: {output_dir}")
                except PermissionError:
                    validator.add_error(
                        f"Cannot create output directory: {output_dir}",
                        suggestions=[
                            "Check directory permissions",
                            "Choose a different output location",
                        ],
                    )
                except Exception as e:
                    validator.add_error(f"Error creating output directory: {e}")

        # Check for potential overwrites
        if not args.output and not args.output_dir:
            # Default behavior: same directory as input
            existing_outputs = []
            for input_file in input_files:
                potential_output = input_file.with_suffix(".pdf")
                if potential_output.exists():
                    existing_outputs.append(potential_output)

            if existing_outputs:
                validator.add_warning(
                    f"The following PDF files will be overwritten: {', '.join(str(f) for f in existing_outputs)}"
                )

        # Raise errors if any
        if validator.has_errors():
            raise CLIError(validator.format_errors())

        # Log warnings
        for warning in validator.warnings:
            self.logger.warning(f"⚠️  {warning}")

    def _validate_css_file(self, css_path: str) -> Path:
        """Validate additional CSS file.

        Args:
            css_path: Path to CSS file

        Returns:
            Validated Path object

        Raises:
            CLIError: If CSS file is invalid
        """
        path = Path(css_path)

        if not path.exists():
            raise CLIError(
                f"CSS file not found: {css_path}",
                suggestions=[
                    "Check if the file path is correct",
                    "Ensure the CSS file exists",
                ],
            )

        if not path.is_file():
            raise CLIError(
                f"CSS path is not a file: {css_path}",
                suggestions=["Ensure the path points to a file, not a directory"],
            )

        if path.suffix.lower() != ".css":
            self.logger.warning(f"⚠️  File '{css_path}' does not have .css extension")

        # Try to read the file
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
                if not content.strip():
                    self.logger.warning(f"⚠️  CSS file '{css_path}' is empty")
        except Exception as e:
            raise CLIError(
                f"Cannot read CSS file '{css_path}': {e}",
                suggestions=[
                    "Check file permissions",
                    "Ensure the file is not corrupted",
                ],
            )

        return path

    def _determine_output_path(
        self,
        input_file: Path,
        output_arg: Optional[str],
        output_dir_arg: Optional[str],
        is_single_file: bool,
    ) -> Path:
        """Determine output path for a given input file.

        Args:
            input_file: Input markdown file
            output_arg: --output argument value
            output_dir_arg: --output-dir argument value
            is_single_file: Whether processing single file

        Returns:
            Output PDF path

        Raises:
            CLIError: If output path is invalid
        """
        if output_arg:
            output_path = Path(output_arg)

            # For single file, treat as exact output path
            if is_single_file:
                if output_path.is_dir():
                    # If directory provided, use input filename
                    return output_path / f"{input_file.stem}.pdf"
                else:
                    # Ensure PDF extension
                    if output_path.suffix.lower() != ".pdf":
                        return output_path.with_suffix(".pdf")
                    return output_path
            else:
                # For multiple files, treat as directory
                if output_path.exists() and output_path.is_file():
                    raise CLIError(f"Cannot use file as output directory: {output_arg}")

                output_path.mkdir(parents=True, exist_ok=True)
                return output_path / f"{input_file.stem}.pdf"

        elif output_dir_arg:
            output_dir = Path(output_dir_arg)
            output_dir.mkdir(parents=True, exist_ok=True)
            return output_dir / f"{input_file.stem}.pdf"

        else:
            # Default: same directory as input with .pdf extension
            return input_file.with_suffix(".pdf")

    def _setup_converter(self, args: argparse.Namespace) -> MarkdownToPDFConverter:
        """Set up the converter with CLI arguments.

        Args:
            args: Parsed command line arguments

        Returns:
            Configured converter

        Raises:
            CLIError: If converter setup fails
        """
        try:
            # Theme configuration
            theme_config_path = None
            if args.theme and not args.no_theme:
                theme_config_path = self._validate_theme_file(
                    args.theme, getattr(args, "strict", False)
                )

            # Extensions
            extensions: Optional[List[Union[str, Extension]]] = None
            if args.extensions is not None:
                extensions = args.extensions
            elif args.no_components:
                # Default extensions without custom components
                extensions = ["tables", "fenced_code", "codehilite"]

            # Create converter
            converter = MarkdownToPDFConverter(
                theme_config_path=theme_config_path, extensions=extensions
            )

            self.logger.debug("Converter initialized successfully")
            return converter

        except Exception as e:
            raise CLIError(
                f"Failed to initialize converter: {e}",
                suggestions=[
                    "Check your theme configuration is valid",
                    "Ensure all required dependencies are installed",
                    "Run with --debug for more detailed error information",
                ],
            )

    def _convert_file(
        self,
        input_file: Path,
        output_file: Path,
        title: Optional[str] = None,
        dry_run: bool = False,
    ) -> bool:
        """Convert a single file with enhanced error handling.

        Args:
            input_file: Input markdown file
            output_file: Output PDF file
            title: Document title override
            dry_run: Whether to perform dry run

        Returns:
            True if successful, False otherwise
        """
        try:
            if dry_run:
                self.logger.info(f"Would convert: {input_file} -> {output_file}")
                return True

            self.logger.info(f"Converting: {input_file} -> {output_file}")

            # Ensure output directory exists
            output_file.parent.mkdir(parents=True, exist_ok=True)

            # Use title from CLI or derive from filename
            doc_title = (
                title or input_file.stem.replace("_", " ").replace("-", " ").title()
            )

            # Convert file
            if self.converter is None:
                raise CLIError("Converter not initialized")

            self.converter.convert_file(input_file, output_file)

            # Report success
            if output_file.exists():
                file_size = output_file.stat().st_size
                self.logger.info(f"✅ Success: {output_file} ({file_size:,} bytes)")
                return True
            else:
                self.logger.error(f"❌ Output file not created: {output_file}")
                return False

        except PermissionError as e:
            self.logger.error(f"❌ Permission error for {input_file}: {e}")
            self.logger.error(
                "💡 Try running with appropriate permissions or choose a different output location"
            )
            return False
        except Exception as e:
            self.logger.error(f"❌ Failed to convert {input_file}: {e}")
            if self.logger.level <= logging.DEBUG:
                self.logger.debug("Full error traceback:")
                self.logger.debug(traceback.format_exc())
            return False

    def run(self, args: Optional[List[str]] = None) -> int:
        """Run the CLI with given arguments.

        Args:
            args: Command line arguments (uses sys.argv if None)

        Returns:
            Exit code (0 for success, non-zero for error)
        """
        parsed_args = None
        try:
            parser = self.create_parser()
            parsed_args = parser.parse_args(args)

            # Configure logging based on verbosity
            if parsed_args.debug:
                self.logger.setLevel(logging.DEBUG)
            elif parsed_args.verbose:
                self.logger.setLevel(logging.INFO)
            elif parsed_args.quiet:
                self.logger.setLevel(logging.ERROR)

            strict_mode = getattr(parsed_args, "strict", False)

            # Handle validation-only mode
            if parsed_args.validate:
                if not parsed_args.theme:
                    raise CLIError(
                        "--validate requires --theme to be specified",
                        suggestions=[
                            "Specify a theme file with --theme path/to/theme.yaml",
                            "Use --help to see usage examples",
                        ],
                    )

                theme_path = self._validate_theme_file(parsed_args.theme, strict_mode)
                self.logger.info(f"✅ Theme file is valid: {theme_path}")
                return 0

            # Check input files are provided for non-validation modes
            if not parsed_args.input_files:
                raise CLIError(
                    "Input files are required for conversion",
                    suggestions=[
                        "Provide at least one Markdown file path",
                        "Use glob patterns like '*.md' to process multiple files",
                        "Run with --help to see usage examples",
                    ],
                )

            # Validate input files
            input_files = self._validate_input_files(
                parsed_args.input_files, strict_mode
            )
            is_single_file = len(input_files) == 1

            # Validate output options
            self._validate_output_options(parsed_args, input_files)

            # Validate CSS file if provided
            if parsed_args.css:
                self._validate_css_file(parsed_args.css)

            self.logger.debug(f"Found {len(input_files)} input file(s)")

            # Set up converter
            self.converter = self._setup_converter(parsed_args)

            # Convert files
            success_count = 0
            total_count = len(input_files)

            for input_file in input_files:
                output_file = self._determine_output_path(
                    input_file,
                    parsed_args.output,
                    parsed_args.output_dir,
                    is_single_file,
                )

                success = self._convert_file(
                    input_file, output_file, parsed_args.title, parsed_args.dry_run
                )

                if success:
                    success_count += 1

            # Report results
            if success_count == total_count:
                self.logger.info(
                    f"🎉 All {total_count} file(s) converted successfully!"
                )
                return 0
            else:
                self.logger.error(
                    f"💥 {success_count}/{total_count} file(s) converted successfully"
                )
                return 1

        except CLIError as e:
            self.logger.error(str(e))
            return getattr(e, "exit_code", 1)
        except KeyboardInterrupt:
            self.logger.info("Operation cancelled by user")
            return 130
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            if parsed_args and getattr(parsed_args, "debug", False):
                self.logger.error("Full error traceback:")
                self.logger.error(traceback.format_exc())
            else:
                self.logger.error("💡 Use --debug for detailed error information")
            return 1


def main():
    """Main entry point for the CLI."""
    cli = MarkdownToPDFCLI()
    return cli.run()


if __name__ == "__main__":
    sys.exit(main())
