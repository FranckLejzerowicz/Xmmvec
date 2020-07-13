# ----------------------------------------------------------------------------
# Copyright (c) 2020, Franck Lejzerowicz.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import os
from os.path import abspath, dirname, isfile, isdir
import pandas as pd
import numpy as np
import altair as alt


def check_path(path: str) -> str:
    if isfile(path):
        return abspath(path)
    else:
        raise IOError('No file named "%s' % path)


def get_name(p_omic_name: str, omic: str) -> str:
    if p_omic_name:
        return p_omic_name
    else:
        return omic


def get_metadata(omic_metadata_fp: str, p_omic_column: str, omic: str) -> (pd.DataFrame, str):
    omic_metadata = pd.DataFrame()
    omic_column = ''
    if omic_metadata_fp:
        with open(omic_metadata_fp) as f:
            for line in f:
                break
        omic_metadata = pd.read_csv(
            omic_metadata_fp, header=0, sep='\t',
            dtype={line.split('\t')[0]: str}
        )
        omic_metadata = omic_metadata.rename(columns={omic_metadata.columns.tolist()[0]: omic})
        if p_omic_column and p_omic_column in omic_metadata.columns.tolist()[1:]:
            omic_column = p_omic_column
    return omic_metadata, omic_column


def merge_metadata(ranks_pd: pd.DataFrame,
                   omic_metadata: pd.DataFrame,
                   omic_column: str, omic: str) -> (pd.DataFrame, str):
    if omic_column:
        ranks_pd = ranks_pd.merge(omic_metadata[[omic, omic_column]], on=omic, how='left')
        omic_column_new = '%s_%s' % (omic_column, omic)
        ranks_pd.rename(columns={omic_column: omic_column_new}, inplace=True)
    else:
        omic_column_new = ''
    return ranks_pd, omic_column_new


def add_ranks(ranks_pd: pd.DataFrame, omic: str) -> pd.DataFrame:
    new_cols = []
    for feat, feat_pd_ in ranks_pd.groupby(omic):
        feat_pd = feat_pd_.copy()
        feat_pd['conditionals_per_%s' % omic] = feat_pd['conditionals'].rank()
        new_cols.append(feat_pd)
    return pd.concat(new_cols)


def get_stacked(ranks_pd: pd.DataFrame, omic1_column: str,
                omic2_column: str, omic1: str, omic2: str) -> pd.DataFrame:
    if omic1_column and omic2_column:
        ranks_st = ranks_pd.set_index(
            [omic1, omic2, omic1_column, omic2_column]
        ).stack().reset_index().rename(
            columns={'level_4': 'conditional', 0: 'rank'}
        )
    elif omic1_column:
        ranks_st = ranks_pd.set_index(
            [omic1, omic2, omic1_column]
        ).stack().reset_index().rename(
            columns={'level_3': 'conditional', 0: 'rank'}
        )
    elif omic2_column:
        ranks_st = ranks_pd.set_index(
            [omic1, omic2, omic2_column]
        ).stack().reset_index().rename(
            columns={'level_3': 'conditional', 0: 'rank'}
        )
    else:
        ranks_st = ranks_pd.set_index(
            [omic1, omic2]
        ).stack().reset_index().rename(
            columns={'level_2': 'conditional', 0: 'rank'}
        )
    return ranks_st


def get_sorted(ranks_st: pd.DataFrame, omic_column: str, omic: str) -> list:
    sorted_omic = sorted(ranks_st[omic].unique())
    if omic_column:
        sorted_omic = [
            feature for group in ranks_st[omic_column].unique().tolist()
            for feature in sorted(ranks_st.query('%s == "%s"' % (omic_column, group))[omic].unique())]
    return sorted_omic


def get_bar_chart(ranks_st: pd.DataFrame, sorted_omic: list,
                  conditionals_1: str, conditionals_2: str,
                  omic_column: str, omic: str, omic1: str,
                  omic2: str, x_size: float, y_size: float,
                  mlt, selector1, selector2):

    if omic == omic1:
        x = alt.X('%s:N' % omic1, sort=sorted_omic, axis=None)
        y = alt.Y('mean(rank):Q', axis=alt.Axis(titleFontSize=6))
        width = x_size
        height = 50
        conditionals_omic = conditionals_1
    else:
        x = alt.X('mean(rank):Q', axis=alt.Axis(titleFontSize=6, orient='top'))
        y = alt.Y('%s:N' % omic2, sort=sorted_omic, axis=None)
        width = 50
        height = y_size
        conditionals_omic = conditionals_2

    if omic_column:
        color = alt.condition(mlt, omic_column, alt.ColorValue("grey"))
    else:
        color = alt.condition(mlt, alt.ColorValue("steelblue"), alt.ColorValue("grey"))

    bar_omic = alt.Chart(ranks_st).mark_bar().encode(
        x=x, y=y, color=color, tooltip=[
            omic, 'mean(rank)', 'stdev(rank)',
            'min(%s)' % conditionals_omic]
    ).add_selection(
        mlt, selector1, selector2
    ).transform_filter(
        alt.FieldEqualPredicate(field='conditional', equal='conditionals')
    ).transform_filter(
        alt.datum[conditionals_1] <= selector1.cutoff
    ).transform_filter(
        alt.datum[conditionals_2] <= selector2.cutoff2
    ).properties(
        width=width,
        height=height
    )
    return bar_omic


def make_figure(ranks_pd: pd.DataFrame, o_ranks_explored: str,
                p_pair_number: int, omic1_column: str,
                omic2_column: str, omic1: str, omic2: str) -> None:

    conditionals_1 = 'conditionals_per_%s' % omic1
    conditionals_2 = 'conditionals_per_%s' % omic2

    ranks_pd2merge = ranks_pd[[omic1, omic2, conditionals_1, conditionals_2]]
    ranks_st = get_stacked(ranks_pd, omic1_column, omic2_column, omic1, omic2)
    ranks_st = ranks_st.merge(ranks_pd2merge, on=[omic1, omic2], how='left')

    conditionals = ['conditionals', 'ranked_conditionals', conditionals_1, conditionals_2]
    conditionals_radio = alt.binding_radio(options=conditionals)
    conditionals_select = alt.selection_single(
        fields=['conditional'], bind=conditionals_radio,
        name="Conditional", init={'conditional': 'conditionals'})

    max_rank1 = int(ranks_st[conditionals_1].max())
    slider1 = alt.binding_range(min=1, max=max_rank1, step=1, name='max. rank of %s per each %s:' % (omic2, omic1))
    selector1 = alt.selection_single(name="cutoff1", fields=['cutoff'], bind=slider1, init={'cutoff': p_pair_number})

    max_rank2 = int(ranks_st[conditionals_2].max())
    slider2 = alt.binding_range(min=1, max=max_rank2, step=1,name='max. rank of %s per each %s:' % (omic1, omic2))
    selector2 = alt.selection_single(name="cutoff2", fields=['cutoff2'], bind=slider2, init={'cutoff2': p_pair_number})

    mlt1 = alt.selection_multi(fields=[omic1], toggle=True)
    mlt2 = alt.selection_multi(fields=[omic2], toggle=True)
    sorted_omic1 = get_sorted(ranks_st, omic1_column, omic1)
    sorted_omic2 = get_sorted(ranks_st, omic2_column, omic2)

    x_size = len(sorted_omic1) * 4
    y_size = len(sorted_omic2) * 4
    rect = alt.Chart(ranks_st).mark_rect().encode(
        x=alt.X('%s:O' % omic1, sort=sorted_omic1,
                axis=alt.Axis(labelOverlap=False, labelFontSize=8,
                              orient='top', labelAngle=45, titleFontSize=6)),
        y=alt.Y('%s:O' % omic2, sort=sorted_omic2,
                axis=alt.Axis(labelOverlap=False, labelFontSize=8, titleFontSize=6)),
        color=alt.Color('rank:Q', legend=alt.Legend(orient='left'),
                        scale=alt.Scale(scheme='rainbow')),
        tooltip=[omic1, omic2, 'conditional', 'rank',
                 conditionals_1, conditionals_2]
    ).transform_filter(
        conditionals_select
    ).transform_filter(
        mlt1
    ).transform_filter(
        mlt2
    ).transform_filter(
        alt.datum[conditionals_1] <= selector1.cutoff
    ).transform_filter(
        alt.datum[conditionals_2] <= selector2.cutoff2
    ).add_selection(
        conditionals_select, mlt1, mlt2, selector1, selector2
    ).properties(
        width=x_size, height=y_size
    )

    bar_omic1 = get_bar_chart(ranks_st, sorted_omic1, conditionals_1, conditionals_2,
                              omic1_column, omic1, omic1, omic2, x_size, y_size,
                              mlt1, selector1, selector2)
    bar_omic2 = get_bar_chart(ranks_st, sorted_omic2, conditionals_1, conditionals_2,
                              omic2_column, omic2, omic1, omic2, x_size, y_size,
                              mlt2, selector1, selector2)
    chart = alt.vconcat(
        alt.hconcat(rect, bar_omic2), bar_omic1
    ).resolve_legend(
        color="independent", size="independent"
    ).configure_axis(
        labelLimit=300, labelFontSize=6,
    ).configure_legend(
        labelLimit=1000, labelFontSize=6, titleFontSize=6, symbolSize=10
    )

    if not isdir(dirname(o_ranks_explored)):
        os.makedirs(dirname(o_ranks_explored))
    chart.save(o_ranks_explored)


def xmmvec(
    i_ranks_path: str,
    o_ranks_explored: str,
    i_tree_taxonomy: str,
    p_omic1_metadata: str,
    p_omic1_column: str,
    p_omic1_name: str,
    p_omic2_metadata: str,
    p_omic2_column: str,
    p_omic2_name: str,
    p_min_probability: float,
    p_pair_number: int
):
    i_ranks_path = check_path(i_ranks_path)
    ranks_pd = pd.read_csv(i_ranks_path, header=0, index_col=0, sep='\t')
    ranks_pd[ranks_pd < p_min_probability] = np.nan
    ranks_pd = ranks_pd.loc[(~ranks_pd.isna().all(1)),
                            (~ranks_pd.isna().all())]

    omic1 = get_name(p_omic1_name, 'omic1')
    omic2 = get_name(p_omic2_name, 'omic2')

    ranks_pd = ranks_pd.unstack().reset_index().rename(
        columns={'level_0': omic1, 'featureid': omic2, 0: 'conditionals'})

    if i_tree_taxonomy:
        i_tree_taxonomy = check_path(i_tree_taxonomy)

    omic1_metadata, omic1_column = get_metadata(p_omic1_metadata, p_omic1_column, omic1)
    omic2_metadata, omic2_column = get_metadata(p_omic2_metadata, p_omic2_column, omic2)

    ranks_pd, omic1_column_new = merge_metadata(ranks_pd, omic1_metadata, omic1_column, omic1)
    ranks_pd, omic2_column_new = merge_metadata(ranks_pd, omic2_metadata, omic2_column, omic2)

    ranks_pd['ranked_conditionals'] = ranks_pd.conditionals.rank()
    ranks_pd = add_ranks(ranks_pd, omic1)
    ranks_pd = add_ranks(ranks_pd, omic2)

    make_figure(ranks_pd, abspath(o_ranks_explored), p_pair_number,
                omic1_column_new, omic2_column_new, omic1, omic2)
