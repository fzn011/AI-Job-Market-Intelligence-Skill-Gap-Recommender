"""Tests for UI theme helpers."""

from __future__ import annotations

import plotly.express as px
import plotly.graph_objects as go
import pytest

from src.ui_theme import style_plotly_figure


def test_style_plotly_figure_pie_chart_uses_colors_not_color():
    """Pie charts must use marker.colors; marker.color raises in Plotly."""
    df = __import__("pandas").DataFrame({"category": ["A", "B", "C"], "count": [3, 2, 1]})
    fig = px.pie(df, names="category", values="count")
    styled = style_plotly_figure(fig)

    assert styled.data
    pie_trace = styled.data[0]
    assert pie_trace.type == "pie"
    assert pie_trace.marker.colors is not None


def test_style_plotly_figure_bar_chart_still_styles_markers():
    df = __import__("pandas").DataFrame({"x": ["a", "b"], "y": [1, 2]})
    fig = px.bar(df, x="x", y="y")
    styled = style_plotly_figure(fig)
    assert styled.data[0].marker.color is not None


def test_style_plotly_figure_preserves_existing_scatter_colors():
    df = __import__("pandas").DataFrame(
        {"x": [1, 2, 3, 4], "y": [1, 2, 3, 4], "group": ["A", "A", "B", "B"]}
    )
    fig = px.scatter(df, x="x", y="y", color="group")
    original_colors = [trace.marker.color for trace in fig.data if trace.marker.color]
    styled = style_plotly_figure(fig)
    styled_colors = [trace.marker.color for trace in styled.data if trace.marker.color]
    assert styled_colors == original_colors
