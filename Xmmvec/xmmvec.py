# ----------------------------------------------------------------------------
# Copyright (c) 2020, Franck Lejzerowicz.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import os
from os.path import abspath, dirname, isfile, isdir, splitext
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


def get_subset(ranks_pd: pd.DataFrame, subset_regex_fp: str, axis: int) -> pd.DataFrame:
    subset_regex = [x.strip() for x in open(subset_regex_fp).readlines()]
    to_keep_feats = {}
    for regex in subset_regex:
        if axis:
            to_keep_feats[regex.lower()] = ranks_pd.index.str.lower().str.contains(regex.lower())
        else:
            to_keep_feats[regex.lower()] = ranks_pd.columns.str.lower().str.contains(regex.lower())
    to_keep_feats_pd = pd.DataFrame(to_keep_feats)
    to_keep_feats = to_keep_feats_pd.any(axis=1)
    print(subset_regex)
    print(to_keep_feats)
    if axis:
        ranks_pd = ranks_pd.loc[ranks_pd.index[to_keep_feats].tolist(), :]
    else:
        ranks_pd = ranks_pd.loc[:, ranks_pd.columns[to_keep_feats].tolist(), :]
    return ranks_pd


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
        omic_metadata.columns = [x.replace('\n', '') for x in omic_metadata.columns]
        if p_omic_column and p_omic_column in omic_metadata.columns.tolist()[1:]:
            omic_column = p_omic_column
    return omic_metadata, omic_column


def get_sign_val(p_omic_value: str) -> list:
    signs_vals = []
    for p_omic_val in p_omic_value:
        if p_omic_val[:2] in ['<=', '>=']:
            sign = p_omic_val[:2]
            val = p_omic_val[2:]
        elif p_omic_val[0] in ['<', '>']:
            sign = p_omic_val[0]
            val = p_omic_val[1:]
        try:
            signs_vals.append([sign, float(val)])
        except TypeError:
            raise TypeError('%s in %s must be numeric' % (val, p_omic_value))
    return signs_vals


def get_filter(omic_metadata: pd.DataFrame, p_omic_filt: str, p_omic_value: str,
               p_omic_quant: float, p_omic_value_regex: str):
    if p_omic_filt:
        if p_omic_filt in omic_metadata.columns:
            pass
        elif p_omic_filt.replace('\\n', '') in omic_metadata.columns:
            p_omic_filt = p_omic_filt.replace('\\n', '')
        else:
            return omic_metadata
        omic_metadata_col = omic_metadata[p_omic_filt].copy()
        if p_omic_quant:
            if p_omic_quant < 0 or p_omic_quant > 100:
                raise IOError('Quantile must be between 0 and 100, not', p_omic_quant)
            if str(omic_metadata_col.dtype) == 'float64':
                q = omic_metadata_col.quantile(q=p_omic_quant/100)
                omic_metadata_col = omic_metadata_col[omic_metadata_col > q]
                omic_metadata = omic_metadata.loc[omic_metadata_col.index, :]
        if p_omic_value:
            if len([1 for x in p_omic_value if x[0] in ['<', '>']]):
                signs_vals = get_sign_val(p_omic_value)
                filt = get_col_bool_sign(omic_metadata_col, signs_vals)
            else:
                if not len([x for x in p_omic_value if x in omic_metadata_col.values]):
                    raise IndexError('None of "%s" in column "%s"' % (', '.join(list(p_omic_value)), p_omic_filt))
                filt = omic_metadata_col.isin([x for x in p_omic_value])
            omic_metadata = omic_metadata[filt]
        if p_omic_value_regex:
            value_regex = [x.strip() for x in open(p_omic_value_regex).readlines()]
            to_keep_feats = {}
            for regex in value_regex:
                to_keep_feats[regex.lower()] = omic_metadata_col.str.lower().str.contains(regex.lower())
            to_keep_feats_pd = pd.DataFrame(to_keep_feats)
            to_keep_feats = to_keep_feats_pd.any(axis=1)
            omic_metadata = omic_metadata.loc[to_keep_feats, :]
        return omic_metadata
    else:
        return omic_metadata


def get_col_bool_sign(omic_metadata_col: pd.Series, signs_vals: list) -> pd.Series:

    if signs_vals[0][0] == '<':
        omic_metadata_bool = omic_metadata_col.astype(float) < signs_vals[0][1]
    elif signs_vals[0][0] == '>':
        omic_metadata_bool = omic_metadata_col.astype(float) > signs_vals[0][1]
    elif signs_vals[0][0] == '<=':
        omic_metadata_bool = omic_metadata_col.astype(float) <= signs_vals[0][1]
    elif signs_vals[0][0] == '>=':
        omic_metadata_bool = omic_metadata_col.astype(float) >= signs_vals[0][1]
    else:
        raise IOError("Sign %s none of ['<', '>', '<=', '>=']" % signs_vals[0][0])

    if len(signs_vals) == 2:
        if signs_vals[1][0] == '<':
            omic_metadata_bool2 = omic_metadata_col.astype(float) < signs_vals[1][1]
        elif signs_vals[1][0] == '>':
            omic_metadata_bool2 = omic_metadata_col.astype(float) > signs_vals[1][1]
        elif signs_vals[1][0] == '<=':
            omic_metadata_bool2 = omic_metadata_col.astype(float) <= signs_vals[1][1]
        elif signs_vals[1][0] == '>=':
            omic_metadata_bool2 = omic_metadata_col.astype(float) >= signs_vals[1][1]
        else:
            raise IOError("Sign %s none of ['<', '>', '<=', '>=']" % signs_vals[1][0])
        return omic_metadata_bool & omic_metadata_bool2
    else:
        return omic_metadata_bool


def merge_metadata(ranks_pd: pd.DataFrame,
                   omic_metadata: pd.DataFrame,
                   omic_column: str, omic: str) -> (pd.DataFrame, str):
    if omic_column:
        ranks_pd = ranks_pd.merge(omic_metadata[[omic, omic_column]], on=omic, how='left')
        omic_column_new = '%s: %s' % (omic, omic_column)
        ranks_pd.rename(columns={omic_column: omic_column_new}, inplace=True)
    else:
        omic_column_new = ''
    return ranks_pd, omic_column_new


def add_ranks(ranks_pd: pd.DataFrame, omic: str) -> pd.DataFrame:
    new_cols = []
    for feat, feat_pd_ in ranks_pd.groupby(omic):
        feat_pd = feat_pd_.copy()
        feat_pd['conditionals_per_%s' % omic] = feat_pd['conditionals'].rank(ascending=False)
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
            for feature in sorted(ranks_st.loc[ranks_st[omic_column] == group, omic].unique())]
    return sorted_omic


def get_bar_chart(ranks_st: pd.DataFrame, sorted_omic: list,
                  conditionals_1: str, conditionals_2: str,
                  omic_column: str, omic: str, omic1: str,
                  omic2: str, x_size: float, y_size: float,
                  mlt, selector1, selector2):

    if omic == omic1:
        x = alt.X('%s:N' % omic1, sort=sorted_omic, axis=None)
        y = alt.Y('mean(rank):Q', axis=alt.Axis(titleFontSize=8))
        width = x_size
        height = 50
    else:
        x = alt.X('mean(rank):Q', axis=alt.Axis(titleFontSize=8, orient='top'))
        y = alt.Y('%s:N' % omic2, sort=sorted_omic, axis=None)
        width = 50
        height = y_size

    if omic_column:
        color = alt.condition(mlt, omic_column, alt.ColorValue("grey"))
    else:
        color = alt.condition(mlt, alt.ColorValue("steelblue"), alt.ColorValue("grey"))

    tooltips = [
        omic, 'mean(rank)', 'stdev(rank)',
        'min(%s)' % conditionals_1,
        'min(%s)' % conditionals_2]
    if omic_column:
        tooltips.append(omic_column)

    bar_omic = alt.Chart(ranks_st).mark_bar().encode(
        x=x, y=y, color=color, tooltip=tooltips
    ).add_selection(
        mlt, selector1, selector2
    ).transform_filter(
        alt.FieldEqualPredicate(field='conditional', equal='conditionals')
    ).transform_filter(
        alt.datum[conditionals_1] <= selector1.cutoff1
    ).transform_filter(
        alt.datum[conditionals_2] <= selector2.cutoff2
    ).properties(
        width=width,
        height=height
    )
    return bar_omic


def make_figure(ranks_pd: pd.DataFrame, o_ranks_explored: str,
                p_pair_number: int, p_color_palette: str, omic1_column: str,
                omic2_column: str, omic1: str, omic2: str,
                p_omic1_filt: str, p_omic1_value: str,
                p_omic2_filt: str, p_omic2_value: str,
                p_omic1_max: int, p_omic2_max: int, p_color_top: str) -> None:

    conditionals_1 = 'conditionals_per_%s' % omic1
    conditionals_2 = 'conditionals_per_%s' % omic2

    if p_omic1_max:
        ranks_pd = ranks_pd.loc[ranks_pd[conditionals_1] <= p_omic1_max, :]
    if p_omic2_max:
        ranks_pd = ranks_pd.loc[ranks_pd[conditionals_2] <= p_omic2_max, :]

    ranks_pd2merge = ranks_pd[[omic1, omic2, conditionals_1, conditionals_2]]
    ranks_st = get_stacked(ranks_pd, omic1_column, omic2_column, omic1, omic2)
    ranks_st = ranks_st.merge(ranks_pd2merge, on=[omic1, omic2], how='left')

    text = ["\n\nCo-occurrence matrix exploration tool (mmvec)",
            "%s (%s features) vs. %s (%s features)" % (
                omic1, ranks_st[omic1].unique().size,
                omic2, ranks_st[omic2].unique().size)
            ]
    subtext = []
    if p_omic1_filt and p_omic1_value:
        subtext.append("Subset %s for '%s' in '%s'" % (
            omic1, ', '.join(list(p_omic1_value)), p_omic1_filt))
    if p_omic2_filt and p_omic2_value:
        subtext.append("Subset %s for '%s' in '%s'" % (
            omic2, ', '.join(list(p_omic1_value)), p_omic2_filt))

    conditionals = ['conditionals', 'ranked_conditionals', conditionals_1, conditionals_2]
    conditionals_radio = alt.binding_radio(options=conditionals, name="Co-occurrence measure")
    conditionals_select = alt.selection_single(
        fields=['conditional'],
        bind=conditionals_radio,
        init={'conditional': 'conditionals'}
    )

    max_rank1 = int(ranks_st[conditionals_1].max())
    init1 = p_pair_number
    if p_pair_number > max_rank1:
        init1 = max_rank1
    slider1 = alt.binding_range(min=1, max=max_rank1, step=1,
                                name='max. rank of %s per each %s:' % (omic2, omic1))
    selector1 = alt.selection_single(name="cutoff1", fields=['cutoff1'],
                                     bind=slider1, init={'cutoff1': init1})

    max_rank2 = int(ranks_st[conditionals_2].max())
    init2 = p_pair_number
    if p_pair_number > max_rank2:
        init2 = max_rank2
    slider2 = alt.binding_range(min=1, max=max_rank2, step=1,
                                name='max. rank of %s per each %s:' % (omic1, omic2))
    selector2 = alt.selection_single(name="cutoff2", fields=['cutoff2'],
                                     bind=slider2, init={'cutoff2': init2})

    mlt1 = alt.selection_multi(fields=[omic1], toggle=True)
    mlt2 = alt.selection_multi(fields=[omic2], toggle=True)

    slider_label1 = alt.binding_range(min=0, max=max_rank1, step=1,
                                      name='top %s per %s:' % (omic2, omic1))
    label1 = alt.selection_single(name="cutoff_label1", fields=['cutoff_label1'],
                                  bind=slider_label1, init={'cutoff_label1': 0})
    slider_label2 = alt.binding_range(min=0, max=max_rank2, step=1,
                                      name='top %s per %s:' % (omic1, omic2))
    label2 = alt.selection_single(name="cutoff_label2", fields=['cutoff_label2'],
                                  bind=slider_label2, init={'cutoff_label2': 0})

    sorted_omic1 = get_sorted(ranks_st, omic1_column, omic1)
    sorted_omic2 = get_sorted(ranks_st, omic2_column, omic2)

    tooltips = [omic1, omic2, 'conditional', 'rank',
                conditionals_1, conditionals_2]

    if omic1_column:
        tooltips.append(omic1_column)
    if omic2_column:
        tooltips.append(omic2_column)

    x_size = len(sorted_omic1) * 6
    y_size = len(sorted_omic2) * 6
    rect = alt.Chart(ranks_st).mark_rect().encode(
        x=alt.X('%s:O' % omic1, sort=sorted_omic1,
                axis=alt.Axis(
                    labelOverlap=False, labelFontSize=6,
                    orient='top', labelAngle=45, titleFontSize=0)),
        y=alt.Y('%s:O' % omic2, sort=sorted_omic2,
                axis=alt.Axis(
                    labelOverlap=False, labelFontSize=6, titleFontSize=0)),
        color=alt.Color('rank:Q', legend=alt.Legend(orient='left'), sort="descending",
                        scale=alt.Scale(scheme=p_color_palette)),
        tooltip=tooltips
    ).add_selection(
        conditionals_select, mlt1, mlt2, selector1, selector2
    ).transform_filter(
        conditionals_select
    ).transform_filter(
        mlt1
    ).transform_filter(
        mlt2
    ).transform_filter(
        alt.datum[conditionals_1] <= selector1.cutoff1
    ).transform_filter(
        alt.datum[conditionals_2] <= selector2.cutoff2
    ).properties(
        width=x_size, height=y_size,
    )

    circ = alt.Chart(ranks_st).mark_point(size=5, shape='diamond').encode(
        x=alt.X('%s:O' % omic1, sort=sorted_omic1,
                axis=alt.Axis(
                    labelOverlap=False, labelFontSize=6,
                    orient='top', labelAngle=45, titleFontSize=0)),
        y=alt.Y('%s:O' % omic2, sort=sorted_omic2,
                axis=alt.Axis(
                    labelOverlap=False, labelFontSize=6, titleFontSize=0)),
        color=alt.ColorValue(p_color_top),
        tooltip=tooltips
    ).add_selection(
        label1, label2
    ).transform_filter(
        conditionals_select
    ).transform_filter(
        mlt1
    ).transform_filter(
        mlt2
    ).transform_filter(
        alt.datum[conditionals_1] <= selector1.cutoff1
    ).transform_filter(
        alt.datum[conditionals_2] <= selector2.cutoff2
    ).transform_filter(
        alt.datum[conditionals_1] <= label1.cutoff_label1
    ).transform_filter(
        alt.datum[conditionals_2] <= label2.cutoff_label2
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
        alt.hconcat((rect + circ), bar_omic2),
        bar_omic1
    )

    chart.resolve_legend(
        color="independent",
        size="independent"
    ).configure_axis(
        labelLimit=300, labelFontSize=8,
    ).configure_legend(
        labelLimit=1000, labelFontSize=8,
        titleFontSize=8, symbolSize=12,
        columns=3
    ).properties(
        title={
            "text": text,
            "subtitle": (subtext + ["(based on altair)"]),
            "color": "black",
            "subtitleColor": "grey"
        }
    )

    if not isdir(dirname(o_ranks_explored)):
        os.makedirs(dirname(o_ranks_explored))
    chart.save(o_ranks_explored)
    print('-> Written:', o_ranks_explored)


def filt_ranks(ranks_pd, omic1_metadata, omic1, omic2_metadata, omic2):
    if omic1_metadata.shape[0]:
        ranks_pd = ranks_pd.loc[:,list(set(omic1_metadata[omic1]) & set(ranks_pd.columns))]
    if omic2_metadata.shape[0]:
        ranks_pd = ranks_pd.loc[list(set(omic2_metadata[omic2]) & set(ranks_pd.index)), :]
    return ranks_pd


def xmmvec(
    i_ranks_path: str,
    o_ranks_explored: str,
    i_tree_taxonomy: str,
    p_omic1_metadata: str,
    p_omic1_column: str,
    p_omic1_filt: str,
    p_omic1_value: str,
    p_omic1_value_regex: str,
    p_omic1_quant: float,
    p_omic1_name: str,
    p_omic1_list: str,
    p_omic1_max: int,
    p_omic2_metadata: str,
    p_omic2_column: str,
    p_omic2_filt: str,
    p_omic2_value: str,
    p_omic2_value_regex: str,
    p_omic2_quant: float,
    p_omic2_name: str,
    p_omic2_list: str,
    p_omic2_max: int,
    p_min_probability: float,
    p_pair_number: int,
    p_color_palette: str,
    p_color_top: str,
    verbose: bool

):
    i_ranks_path = check_path(i_ranks_path)
    ranks_pd = pd.read_csv(i_ranks_path, header=0, index_col=0, sep='\t')
    if verbose:
        print('Input matrix:', i_ranks_path)
    omic1 = get_name(p_omic1_name, 'omic1')
    omic2 = get_name(p_omic2_name, 'omic2')
    if verbose:
        print('Dealing with:')
        print(' - omic1 (matrix columns): ', omic1)
        print(' - omic2 (matrix rows):    ', omic2)

    if i_tree_taxonomy:
        i_tree_taxonomy = check_path(i_tree_taxonomy)

    if p_omic1_list:
        ranks_pd = get_subset(ranks_pd, p_omic1_list, 0)
    if p_omic2_list:
        ranks_pd = get_subset(ranks_pd, p_omic2_list, 1)

    omic1_metadata = pd.DataFrame()
    omic2_metadata = pd.DataFrame()
    omic1_column = ''
    omic2_column = ''
    if p_omic1_metadata or p_omic2_metadata:
        if verbose:
            print('Read metadata...', end='')
        omic1_metadata, omic1_column = get_metadata(p_omic1_metadata, p_omic1_column, omic1)
        omic2_metadata, omic2_column = get_metadata(p_omic2_metadata, p_omic2_column, omic2)
        if verbose:
            print('done.')
    if p_omic1_filt or p_omic1_filt:
        if verbose:
            print('Filter using metadata...', end='')
        omic1_metadata = get_filter(omic1_metadata, p_omic1_filt, p_omic1_value, p_omic1_quant, p_omic1_value_regex)
        omic2_metadata = get_filter(omic2_metadata, p_omic2_filt, p_omic2_value, p_omic2_quant, p_omic2_value_regex)
        ranks_pd = filt_ranks(ranks_pd, omic1_metadata, omic1, omic2_metadata, omic2)
        if verbose:
            print('done.')

    if verbose:
        print('Cast ranks as column formatted...', end='')
    ranks_pd[ranks_pd < p_min_probability] = np.nan
    ranks_pd = ranks_pd.loc[(~ranks_pd.isna().all(1)), (~ranks_pd.isna().all())]
    ranks_pd = ranks_pd.unstack().reset_index()
    ranks_pd.columns = [omic1, omic2, 'conditionals']
    ranks_pd[omic1] = ranks_pd[omic1].astype(str)
    ranks_pd[omic2] = ranks_pd[omic2].astype(str)
    ranks_pd['ranked_conditionals'] = ranks_pd.conditionals.rank(ascending=False)
    ranks_pd = add_ranks(ranks_pd, omic1)
    ranks_pd = add_ranks(ranks_pd, omic2)
    if verbose:
        print('done.')

    omic1_column_new = ''
    omic2_column_new = ''
    if omic1_metadata.shape[0] or omic2_metadata.shape[0]:
        if verbose:
            print('Merge metadata...', end='')
        ranks_pd, omic1_column_new = merge_metadata(ranks_pd, omic1_metadata, omic1_column, omic1)
        ranks_pd, omic2_column_new = merge_metadata(ranks_pd, omic2_metadata, omic2_column, omic2)
        if verbose:
            print('done.')

    if o_ranks_explored:
        if o_ranks_explored.endswith('.html'):
            ranks_explored = abspath(o_ranks_explored)
        else:
            raise IOError('Output file name must end with ".html')
    else:
        ranks_explored = '%s-p%s-n%s.html' % (splitext(i_ranks_path)[0], p_min_probability, p_pair_number)

    if verbose:
        print('Make figure:')
    make_figure(ranks_pd, ranks_explored, p_pair_number, p_color_palette,
                omic1_column_new, omic2_column_new, omic1, omic2,
                p_omic1_filt, p_omic1_value, p_omic2_filt, p_omic2_value,
                p_omic1_max, p_omic2_max, p_color_top)
    if verbose:
        print('Completed.')
