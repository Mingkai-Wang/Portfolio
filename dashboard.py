#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Embedded Dash dashboard for electricity consumption visualization
Integrated with Flask application
"""

from dash import Dash, html, dcc, callback, Output, Input
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

def create_dashboard(server):
    """Create and configure the Dash dashboard"""
    
    # Initialize Dash app with Flask server
    dash_app = Dash(__name__, server=server, url_base_pathname='/dashboard/')
    
    # Load the data
    try:
        df = pd.read_csv('static/downloads/electricity_consumption.csv')
    except FileNotFoundError:
        # Create sample data if file doesn't exist
        df = pd.DataFrame({
            'dwelling_type_id': [1, 2, 3, 4, 5, 6] * 10,
            'year': [2020, 2021, 2022, 2023, 2024] * 12,
            'kwh_per_acc': [100, 150, 200, 250, 300, 350] * 10,
            'area': ['Central', 'North', 'South', 'East', 'West'] * 12
        })
    
    # Create dwelling type mapping
    dwelling_type_mapping = {
        1: "1-room / 2-room",
        2: "Private Apartments and Condominiums", 
        3: "Landed Properties",
        4: "5-room and Executive",
        5: "3-room",
        6: "4-room"
    }
    
    # Dashboard layout
    dash_app.layout = html.Div([
        # Header
        html.Div([
            html.H1("Singapore Electricity Consumption Dashboard", 
                   className="text-center mb-4 text-primary"),
            html.P("Interactive visualization of electricity consumption by dwelling type",
                  className="text-center text-muted mb-4")
        ], className="container-fluid bg-light py-3 mb-4"),
        
        # Controls
        html.Div([
            html.Div([
                html.Label('Select Dwelling Type:', className="form-label fw-bold"),
                dcc.Dropdown(
                    id='dwelling-type-dropdown',
                    options=[{'label': f"{dwelling_type_mapping.get(i, f'Type {i}')}", 'value': i} 
                            for i in sorted(df['dwelling_type_id'].unique())],
                    value=df['dwelling_type_id'].iloc[0] if len(df) > 0 else 1,
                    className="mb-3"
                )
            ], className="col-md-6"),
            
            html.Div([
                html.Label('Select Year Range:', className="form-label fw-bold"),
                dcc.RangeSlider(
                    id='year-range-slider',
                    min=int(df['year'].min()) if 'year' in df.columns else 2020,
                    max=int(df['year'].max()) if 'year' in df.columns else 2024,
                    step=1,
                    marks={year: str(year) for year in range(
                        int(df['year'].min()) if 'year' in df.columns else 2020,
                        int(df['year'].max()) + 1 if 'year' in df.columns else 2025
                    )},
                    value=[int(df['year'].min()) if 'year' in df.columns else 2020, 
                           int(df['year'].max()) if 'year' in df.columns else 2024],
                    className="mb-3"
                )
            ], className="col-md-6")
        ], className="row container-fluid mb-4"),
        
        # Charts
        html.Div([
            html.Div([
                dcc.Graph(id='consumption-trend-graph')
            ], className="col-12 mb-4"),
            
            html.Div([
                dcc.Graph(id='consumption-by-area-graph')
            ], className="col-12")
        ], className="row container-fluid")
    ], className="container-fluid")
    
    # Callbacks
    @dash_app.callback(
        [Output('consumption-trend-graph', 'figure'),
         Output('consumption-by-area-graph', 'figure')],
        [Input('dwelling-type-dropdown', 'value'),
         Input('year-range-slider', 'value')]
    )
    def update_graphs(selected_dwelling, year_range):
        # Filter data
        filtered_df = df[df['dwelling_type_id'] == selected_dwelling]
        if year_range and 'year' in df.columns:
            filtered_df = filtered_df[
                (filtered_df['year'] >= year_range[0]) & 
                (filtered_df['year'] <= year_range[1])
            ]
        
        # Trend graph
        if 'year' in filtered_df.columns and len(filtered_df) > 0:
            trend_fig = px.line(
                filtered_df, 
                x='year', 
                y='kwh_per_acc',
                title=f'Electricity Consumption Trend - {dwelling_type_mapping.get(selected_dwelling, f"Type {selected_dwelling}")}',
                labels={'kwh_per_acc': 'kWh per Account', 'year': 'Year'}
            )
            trend_fig.update_layout(
                plot_bgcolor='white',
                paper_bgcolor='white',
                font_color='black'
            )
        else:
            trend_fig = px.line(title="No data available for trend analysis")
        
        # Area graph
        if 'area' in filtered_df.columns and len(filtered_df) > 0:
            area_fig = px.bar(
                filtered_df.groupby('area')['kwh_per_acc'].mean().reset_index(),
                x='area',
                y='kwh_per_acc',
                title=f'Average Consumption by Area - {dwelling_type_mapping.get(selected_dwelling, f"Type {selected_dwelling}")}',
                labels={'kwh_per_acc': 'Average kWh per Account', 'area': 'Area'}
            )
            area_fig.update_layout(
                plot_bgcolor='white',
                paper_bgcolor='white',
                font_color='black'
            )
        else:
            area_fig = px.bar(title="No area data available")
        
        return trend_fig, area_fig
    
    return dash_app