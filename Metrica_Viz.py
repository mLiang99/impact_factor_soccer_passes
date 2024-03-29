#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr  5 09:10:58 2020
Module for visualising Metrica tracking and event data
Data can be found at: https://github.com/metrica-sports/sample-data
UPDATE for tutorial 4: plot_pitchcontrol_for_event no longer requires 'xgrid' and 'ygrid' as inputs.
@author: Laurie Shaw (@EightyFivePoint)
"""

import matplotlib.pyplot as plt
import numpy as np
import matplotlib.animation as animation
import Metrica_IO as mio


def plot_pitch(field_dimen=(106.0, 68.0), field_color='green', linewidth=2, markersize=20):
    """ plot_pitch

    Plots a soccer pitch. All distance units converted to meters.

    Parameters
    -----------
        field_dimen: (length, width) of field in meters. Default is (106,68)
        field_color: color of field. options are {'green','white'}
        linewidth  : width of lines. default = 2
        markersize : size of markers (e.g. penalty spot, centre spot, posts). default = 20

    Returrns
    -----------
       fig,ax : figure and aixs objects (so that other data can be plotted onto the pitch)
    """
    fig, ax = plt.subplots(figsize=(12, 8))  # create a figure
    # decide what color we want the field to be. Default is green, but can also choose white
    if field_color == 'green':
        ax.set_facecolor('mediumseagreen')
        lc = 'whitesmoke'  # line color
        pc = 'w'  # 'spot' colors
    elif field_color == 'white':
        lc = 'k'
        pc = 'k'
    # ALL DIMENSIONS IN m
    border_dimen = (3, 3)  # include a border arround of the field of width 3m
    meters_per_yard = 0.9144  # unit conversion from yards to meters
    half_pitch_length = field_dimen[0]/2.  # length of half pitch
    half_pitch_width = field_dimen[1]/2.  # width of half pitch
    signs = [-1, 1]
    # Soccer field dimensions typically defined in yards, so we need to convert to meters
    goal_line_width = 8*meters_per_yard
    box_width = 20*meters_per_yard
    box_length = 6*meters_per_yard
    area_width = 44*meters_per_yard
    area_length = 18*meters_per_yard
    penalty_spot = 12*meters_per_yard
    corner_radius = 1*meters_per_yard
    D_length = 8*meters_per_yard
    D_radius = 10*meters_per_yard
    D_pos = 12*meters_per_yard
    centre_circle_radius = 10*meters_per_yard
    # plot half way line # center circle
    ax.plot([0, 0], [-half_pitch_width, half_pitch_width], lc, linewidth=linewidth)
    ax.scatter(0.0, 0.0, marker='o', facecolor=lc, linewidth=0, s=markersize)
    y = np.linspace(-1, 1, 50)*centre_circle_radius
    x = np.sqrt(centre_circle_radius**2-y**2)
    ax.plot(x, y, lc, linewidth=linewidth)
    ax.plot(-x, y, lc, linewidth=linewidth)
    for s in signs:  # plots each line seperately
        # plot pitch boundary
        ax.plot([-half_pitch_length, half_pitch_length],
                [s*half_pitch_width, s*half_pitch_width], lc, linewidth=linewidth)
        ax.plot([s*half_pitch_length, s*half_pitch_length],
                [-half_pitch_width, half_pitch_width], lc, linewidth=linewidth)
        # goal posts & line
        ax.plot([s*half_pitch_length, s*half_pitch_length], [-goal_line_width/2., goal_line_width/2.],
                pc+'s', markersize=6*markersize/20., linewidth=linewidth)
        # 6 yard box
        ax.plot([s*half_pitch_length, s*half_pitch_length-s*box_length],
                [box_width/2., box_width/2.], lc, linewidth=linewidth)
        ax.plot([s*half_pitch_length, s*half_pitch_length-s*box_length],
                [-box_width/2., -box_width/2.], lc, linewidth=linewidth)
        ax.plot([s*half_pitch_length-s*box_length, s*half_pitch_length-s*box_length],
                [-box_width/2., box_width/2.], lc, linewidth=linewidth)
        # penalty area
        ax.plot([s*half_pitch_length, s*half_pitch_length-s*area_length],
                [area_width/2., area_width/2.], lc, linewidth=linewidth)
        ax.plot([s*half_pitch_length, s*half_pitch_length-s*area_length],
                [-area_width/2., -area_width/2.], lc, linewidth=linewidth)
        ax.plot([s*half_pitch_length-s*area_length, s*half_pitch_length-s*area_length],
                [-area_width/2., area_width/2.], lc, linewidth=linewidth)
        # penalty spot
        ax.scatter(s*half_pitch_length-s*penalty_spot, 0.0, marker='o', facecolor=lc, linewidth=0, s=markersize)
        # corner flags
        y = np.linspace(0, 1, 50)*corner_radius
        x = np.sqrt(corner_radius**2-y**2)
        ax.plot(s*half_pitch_length-s*x, -half_pitch_width+y, lc, linewidth=linewidth)
        ax.plot(s*half_pitch_length-s*x, half_pitch_width-y, lc, linewidth=linewidth)
        # draw the D
        y = np.linspace(-1, 1, 50)*D_length  # D_length is the chord of the circle that defines the D
        x = np.sqrt(D_radius**2-y**2)+D_pos
        ax.plot(s*half_pitch_length-s*x, y, lc, linewidth=linewidth)

    # remove axis labels and ticks
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.set_xticks([])
    ax.set_yticks([])
    # set axis limits
    xmax = field_dimen[0]/2. + border_dimen[0]
    ymax = field_dimen[1]/2. + border_dimen[1]
    ax.set_xlim([-xmax, xmax])
    ax.set_ylim([-ymax, ymax])
    ax.set_axisbelow(True)
    return fig, ax


def plot_frame(hometeam, awayteam, figax=None, team_colors=('r', 'b'), field_dimen=(106.0, 68.0), include_player_velocities=False, PlayerMarkerSize=10, PlayerAlpha=0.7, annotate=False):
    """ plot_frame( hometeam, awayteam )

    Plots a frame of Metrica tracking data (player positions and the ball) on a football pitch. All distances should be in meters.

    Parameters
    -----------
        hometeam: row (i.e. instant) of the home team tracking data frame
        awayteam: row of the away team tracking data frame
        fig,ax: Can be used to pass in the (fig,ax) objects of a previously generated pitch. Set to (fig,ax) to use an existing figure, or None (the default) to generate a new pitch plot,
        team_colors: Tuple containing the team colors of the home & away team. Default is 'r' (red, home team) and 'b' (blue away team)
        field_dimen: tuple containing the length and width of the pitch in meters. Default is (106,68)
        include_player_velocities: Boolean variable that determines whether player velocities are also plotted (as quivers). Default is False
        PlayerMarkerSize: size of the individual player marlers. Default is 10
        PlayerAlpha: alpha (transparency) of player markers. Defaault is 0.7
        annotate: Boolean variable that determines with player jersey numbers are added to the plot (default is False)

    Returrns
    -----------
       fig,ax : figure and aixs objects (so that other data can be plotted onto the pitch)
    """
    if figax is None:  # create new pitch
        fig, ax = plot_pitch(field_dimen=field_dimen)
    else:  # overlay on a previously generated pitch
        fig, ax = figax  # unpack tuple
    # plot home & away teams in order
    for team, color in zip([hometeam, awayteam], team_colors):
        x_columns = [c for c in team.keys() if c[-2:].lower() == '_x' and c !=
                     'ball_x']  # column header for player x positions
        y_columns = [c for c in team.keys() if c[-2:].lower() == '_y' and c !=
                     'ball_y']  # column header for player y positions
        ax.plot(team[x_columns], team[y_columns], color+'o',
                markersize=PlayerMarkerSize, alpha=PlayerAlpha)  # plot player positions
        if include_player_velocities:
            vx_columns = ['{}_vx'.format(c[:-2]) for c in x_columns]  # column header for player x positions
            vy_columns = ['{}_vy'.format(c[:-2]) for c in y_columns]  # column header for player y positions
            ax.quiver(team[x_columns], team[y_columns], team[vx_columns], team[vy_columns], color=color,
                      scale_units='inches', scale=10., width=0.0015, headlength=5, headwidth=3, alpha=PlayerAlpha)
        if annotate:
            [ax.text(team[x]+0.5, team[y]+0.5, x.split('_')[1], fontsize=10, color=color)
             for x, y in zip(x_columns, y_columns) if not (np.isnan(team[x]) or np.isnan(team[y]))]
    # plot ball
    ax.plot(hometeam['ball_x'], hometeam['ball_y'], 'ko', markersize=6, alpha=1.0, linewidth=0)
    return fig, ax


def plot_events(events, figax=None, field_dimen=(106.0, 68), indicators=['Marker', 'Arrow'], color='r', marker_style='o', alpha=0.5, annotate=False):
    """ plot_events( events )

    Plots Metrica event positions on a football pitch. event data can be a single or several rows of a data frame. All distances should be in meters.

    Parameters xThreat_Pass
    -----------
        events: row (i.e. instant) of the home team tracking data frame
        fig,ax: Can be used to pass in the (fig,ax) objects of a previously generated pitch. Set to (fig,ax) to use an existing figure, or None (the default) to generate a new pitch plot,
        field_dimen: tuple containing the length and width of the pitch in meters. Default is (106,68)
        indicators: List containing choices on how to plot the event. 'Marker' places a marker at the 'Start X/Y' location of the event; 'Arrow' draws an arrow from the start to end locations. Can choose one or both.
        color: color of indicator. Default is 'r' (red)
        marker_style: Marker type used to indicate the event position. Default is 'o' (filled ircle).
        alpha: alpha of event marker. Default is 0.5
        annotate: Boolean determining whether text annotation from event data 'Type' and 'From' fields is shown on plot. Default is False.

    Returrns
    -----------
       fig,ax : figure and aixs objects (so that other data can be plotted onto the pitch)
    """

    if figax is None:  # create new pitch
        fig, ax = plot_pitch(field_dimen=field_dimen)
    else:  # overlay on a previously generated pitch
        fig, ax = figax
    for i, row in events.iterrows():
        if 'Marker' in indicators:
            ax.plot(row['Start X'], row['Start Y'], color+marker_style, alpha=alpha)
        if 'Arrow' in indicators:
            ax.annotate("", xy=row[['End X', 'End Y']], xytext=row[['Start X', 'Start Y']], alpha=alpha, arrowprops=dict(
                alpha=alpha, width=0.5, headlength=4.0, headwidth=4.0, color=color), annotation_clip=False)
        if annotate:
            textstring = str(row['Type_of_Pass'][0].upper()) + ': [ ' + str(round(row['possession_score'], 3)) + '; ' + str(round(row['scoring_score'],3) )+ '; ' + str(round(row['Improved_Impact_Score'],3) ) + " ]"
            ax.text(row['Start X']+alpha, row['Start Y']+alpha, textstring, fontsize=10, color=color)
    return fig, ax


def plot_events2(events, figax=None, field_dimen=(106.0, 68), indicators=['Marker', 'Arrow'], color='r', marker_style='o', alpha=0.5, annotate=False):
    """ plot_events( events )

    Plots Metrica event positions on a football pitch. event data can be a single or several rows of a data frame. All distances should be in meters.

    Parameters
    -----------
        events: row (i.e. instant) of the home team tracking data frame
        fig,ax: Can be used to pass in the (fig,ax) objects of a previously generated pitch. Set to (fig,ax) to use an existing figure, or None (the default) to generate a new pitch plot,
        field_dimen: tuple containing the length and width of the pitch in meters. Default is (106,68)
        indicators: List containing choices on how to plot the event. 'Marker' places a marker at the 'Start X/Y' location of the event; 'Arrow' draws an arrow from the start to end locations. Can choose one or both.
        color: color of indicator. Default is 'r' (red)
        marker_style: Marker type used to indicate the event position. Default is 'o' (filled ircle).
        alpha: alpha of event marker. Default is 0.5
        annotate: Boolean determining whether text annotation from event data 'Type' and 'From' fields is shown on plot. Default is False.

    Returrns
    -----------
       fig,ax : figure and aixs objects (so that other data can be plotted onto the pitch)
    """

    if figax is None:  # create new pitch
        fig, ax = plot_pitch(field_dimen=field_dimen)
    else:  # overlay on a previously generated pitch
        fig, ax = figax
    for i, row in events.iterrows():
        if 'Marker' in indicators:
            ax.plot(row['Start X'], row['Start Y'], color+marker_style, alpha=alpha)
        if 'Arrow' in indicators:
            ax.annotate("", xy=row[['End X', 'End Y']], xytext=row[['Start X', 'Start Y']], alpha=alpha, arrowprops=dict(
                alpha=alpha, width=0.5, headlength=4.0, headwidth=4.0, color=color), annotation_clip=False)
        if annotate:
            if row['Type'] != 'PASS': 
                textstring = ' [ ' + str(row['Subtype'] ) + " ]"
            else:
                textstring = ' [ xT: ' + str(round(row['xThreat_Pass'],3) ) + " ]"
            ax.text(row['Start X'], row['Start Y'], textstring, fontsize=10, color=color)
    return fig, ax

