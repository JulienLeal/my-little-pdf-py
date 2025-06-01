"""
Test the templating system for custom components.
"""

import pytest

from src.md_to_pdf.templating import TemplateManager


def test_template_manager_initialization():
    """Test that TemplateManager initializes correctly."""
    tm = TemplateManager()

    # Should have discovered the templates we created
    registered_components = tm.get_registered_components()
    assert "tip_box" in registered_components
    assert "magic_secret" in registered_components
    assert "attention_box" in registered_components

    # Should be able to check registration
    assert tm.is_component_registered("tip_box")
    assert tm.is_component_registered("magic_secret")
    assert tm.is_component_registered("attention_box")
    assert not tm.is_component_registered("nonexistent_component")


def test_context_building():
    """Test that template context is built correctly."""
    tm = TemplateManager()

    attributes = {"color": "blue", "title": "Test Title", "important": True}
    content = "This is test content"

    context = tm.build_context("tip_box", attributes, content)

    # Check basic context structure
    assert context["component_name"] == "tip_box"
    assert context["content"] == content
    assert context["attributes"] == attributes

    # Check individual attributes are available
    assert context["color"] == "blue"
    assert context["title"] == "Test Title"
    assert context["important"] is True

    # Check computed values
    assert "custom-block" in context["css_classes"]
    assert "tip-box" in context["css_classes"]
    assert "color-blue" in context["css_classes"]

    # Check data attributes
    assert "data-color" in context["data_attributes"]
    assert "data-title" in context["data_attributes"]
    assert "data-important" in context["data_attributes"]


def test_tip_box_rendering():
    """Test rendering a tip_box component."""
    tm = TemplateManager()

    attributes = {"color": "blue", "title": "Pro Tip"}
    content = "This is a helpful tip!"

    html = tm.render_component("tip_box", attributes, content)

    # Check that the HTML contains expected elements
    assert 'class="custom-block tip-box color-blue"' in html
    assert 'data-color="blue"' in html
    assert 'data-title="Pro Tip"' in html
    assert "<strong>Pro Tip</strong>" in html
    assert "This is a helpful tip!" in html
    assert "tip-box-header" in html
    assert "tip-box-content" in html


def test_magic_secret_rendering():
    """Test rendering a magic_secret component."""
    tm = TemplateManager()

    attributes = {"level": "high", "title": "Hidden Knowledge"}
    content = "The secret is revealed!"

    html = tm.render_component("magic_secret", attributes, content)

    # Check that the HTML contains expected elements
    assert 'class="custom-block magic-secret' in html
    assert 'data-level="high"' in html
    assert 'data-title="Hidden Knowledge"' in html
    assert "<strong>Hidden Knowledge</strong>" in html
    assert "The secret is revealed!" in html
    assert "✨" in html  # Magic icons
    assert "magic-secret-header" in html
    assert "magic-secret-content" in html


def test_attention_box_rendering():
    """Test rendering an attention_box component."""
    tm = TemplateManager()

    attributes = {"type": "warning", "title": "Important Notice"}
    content = "Please pay attention to this!"

    html = tm.render_component("attention_box", attributes, content)

    # Check that the HTML contains expected elements
    assert 'class="custom-block attention-box' in html
    assert 'data-type="warning"' in html
    assert 'data-title="Important Notice"' in html
    assert "<strong>Important Notice</strong>" in html
    assert "Please pay attention to this!" in html
    assert "⚠️" in html  # Warning icon
    assert "attention-box-header" in html
    assert "attention-box-content" in html


def test_unregistered_component():
    """Test that rendering an unregistered component raises an error."""
    tm = TemplateManager()

    with pytest.raises(ValueError, match="Component 'nonexistent' is not registered"):
        tm.render_component("nonexistent", {}, "content")


def test_custom_filters():
    """Test that custom Jinja2 filters work correctly."""
    tm = TemplateManager()

    # Test css_class filter
    result = tm.render_from_string("{{ 'test_component' | css_class }}", {})
    assert result == "test-component"

    # Test attr_string filter
    attrs = {"data-test": "value", "disabled": True, "hidden": False}
    template = "{{ attrs | attr_string }}"
    result = tm.render_from_string(template, {"attrs": attrs})
    assert 'data-test="value"' in result
    assert "disabled" in result
    assert "hidden" not in result  # False values should be excluded


def test_component_registration():
    """Test manual component registration."""
    tm = TemplateManager()

    # Register a new component
    tm.register_component("custom_test", "tip_box.html")  # Reuse existing template

    assert tm.is_component_registered("custom_test")
    assert "custom_test" in tm.get_registered_components()

    # Should be able to render with the new name
    html = tm.render_component("custom_test", {"title": "Test"}, "Content")
    assert "custom-block custom-test" in html


if __name__ == "__main__":
    # Run basic tests
    test_template_manager_initialization()
    test_context_building()
    test_tip_box_rendering()
    test_magic_secret_rendering()
    test_attention_box_rendering()
    test_custom_filters()
    test_component_registration()
    print("All templating tests passed!")
